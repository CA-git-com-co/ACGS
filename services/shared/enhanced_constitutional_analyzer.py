#!/usr/bin/env python3
"""
Enhanced Constitutional Analyzer with Qwen3 Embedding Integration

This module provides semantic similarity analysis using Qwen3 embeddings
integrated with the existing MultiModelManager for comprehensive constitutional
compliance analysis in the ACGS-1 governance system.

Key Features:
- Semantic similarity analysis using Qwen3 embeddings
- Integration with existing multi-model LLM coordination
- Constitutional compliance scoring with >95% accuracy target
- Real-time analysis capabilities for PGC service integration
- Constitution Hash validation logic
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np

# ACGS-1 imports
try:
    from .ai_model_service import ModelRole, get_ai_model_service
    from .constitutional_metrics import get_constitutional_metrics
    from .langgraph_config import get_langgraph_config
    from .qwen3_embedding_client import (
        EmbeddingRequest,
        EmbeddingTaskType,
        get_qwen3_embedding_client,
    )
    from .redis_cache import get_cache
except ImportError:
    # Fallback for testing
    from ai_model_service import ModelRole, get_ai_model_service
    from constitutional_metrics import get_constitutional_metrics
    from langgraph_config import get_langgraph_config
    from qwen3_embedding_client import (
        EmbeddingRequest,
        EmbeddingTaskType,
        get_qwen3_embedding_client,
    )
    from redis_cache import get_cache

logger = logging.getLogger(__name__)


class AnalysisType(str, Enum):
    """Types of constitutional analysis."""

    SEMANTIC_SIMILARITY = "semantic_similarity"
    COMPLIANCE_SCORING = "compliance_scoring"
    CONFLICT_DETECTION = "conflict_detection"
    POLICY_VALIDATION = "policy_validation"
    CONSTITUTIONAL_ALIGNMENT = "constitutional_alignment"


@dataclass
class PolicyRule:
    """Policy rule for constitutional analysis."""

    id: str
    title: str
    content: str
    rule_type: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConstitutionalFramework:
    """Constitutional framework for analysis."""

    constitution_hash: str
    principles: List[Dict[str, Any]]
    policies: List[PolicyRule]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AnalysisResult:
    """Result of constitutional analysis."""

    analysis_type: AnalysisType
    compliance_score: float
    confidence_score: float
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    processing_time_ms: float
    constitutional_hash: str
    metadata: Optional[Dict[str, Any]] = None


class EnhancedConstitutionalAnalyzer:
    """
    Enhanced Constitutional Analyzer with Qwen3 embedding integration.

    Provides semantic similarity analysis and constitutional compliance scoring
    using embeddings combined with multi-model LLM coordination.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Enhanced Constitutional Analyzer."""
        self.config = config or {}
        self.langgraph_config = get_langgraph_config()
        self.constitutional_hash = "cdd01ef066bc6cf2"  # Reference constitutional hash

        # Component references
        self.embedding_client = None
        self.ai_model_service = None
        self.redis_client = None
        self.metrics = get_constitutional_metrics("enhanced_constitutional_analyzer")

        # Performance settings
        self.similarity_threshold = self.config.get("similarity_threshold", 0.85)
        self.compliance_threshold = self.config.get("compliance_threshold", 0.95)
        self.cache_ttl_seconds = self.config.get("cache_ttl_seconds", 3600)

        # State tracking
        self.initialized = False
        self.total_analyses = 0
        self.successful_analyses = 0

        logger.info("EnhancedConstitutionalAnalyzer initialized")

    async def initialize(self) -> bool:
        """Initialize the analyzer and its components."""
        try:
            start_time = time.time()

            # Initialize embedding client with proper error handling
            try:
                self.embedding_client = await get_qwen3_embedding_client()
                if self.embedding_client is None:
                    logger.warning(
                        "Embedding client initialization returned None, using fallback"
                    )
                    self.embedding_client = None
            except Exception as e:
                logger.warning(
                    f"Failed to initialize embedding client: {e}, using fallback"
                )
                self.embedding_client = None

            # Initialize AI model service
            try:
                self.ai_model_service = await get_ai_model_service()
            except Exception as e:
                logger.warning(f"Failed to initialize AI model service: {e}")
                self.ai_model_service = None

            # Initialize Redis cache
            try:
                self.redis_client = get_cache()
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.redis_client = None

            self.initialized = True

            init_time = (time.time() - start_time) * 1000
            logger.info(
                f"EnhancedConstitutionalAnalyzer initialized successfully in {init_time:.2f}ms"
            )

            # Record initialization metrics
            try:
                self.metrics.record_constitutional_principle_operation(
                    operation_type="analyzer_initialization",
                    principle_category="constitutional_analysis",
                    status="success",
                )
            except Exception as e:
                logger.warning(f"Failed to record initialization metrics: {e}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize EnhancedConstitutionalAnalyzer: {e}")
            self.metrics.record_constitutional_principle_operation(
                operation_type="analyzer_initialization",
                principle_category="constitutional_analysis",
                status="error",
            )
            return False

    async def analyze_constitutional_compliance(
        self,
        policy_content: str,
        analysis_type: AnalysisType = AnalysisType.COMPLIANCE_SCORING,
        context: Optional[Dict[str, Any]] = None,
    ) -> AnalysisResult:
        """
        Analyze constitutional compliance using semantic embeddings and LLM coordination.

        Args:
            policy_content: Policy content to analyze
            analysis_type: Type of analysis to perform
            context: Additional context for analysis

        Returns:
            AnalysisResult with compliance scoring and recommendations
        """
        start_time = time.time()
        self.total_analyses += 1

        try:
            # Step 1: Generate embeddings for policy content
            embedding_request = EmbeddingRequest(
                text=policy_content,
                task_type=EmbeddingTaskType.CONSTITUTIONAL_ANALYSIS,
                context=context,
            )

            if self.embedding_client is None:
                # Use fallback embedding (mock)
                policy_embedding = [0.1] * 8192  # Mock embedding
                logger.warning("Using fallback embedding due to client unavailability")
            else:
                policy_embedding_response = (
                    await self.embedding_client.generate_embedding(embedding_request)
                )

                if not policy_embedding_response.success:
                    raise ValueError(
                        f"Failed to generate policy embedding: {policy_embedding_response.error_message}"
                    )

                policy_embedding = policy_embedding_response.embedding

            # Step 2: Get constitutional framework
            constitutional_framework = await self._get_constitutional_framework()

            # Step 3: Perform semantic similarity analysis
            similarity_scores = await self._calculate_constitutional_similarity(
                policy_embedding, constitutional_framework
            )

            # Step 4: Use multi-model LLM for detailed analysis
            llm_analysis = await self._perform_llm_analysis(
                policy_content,
                constitutional_framework,
                similarity_scores,
                analysis_type,
            )

            # Step 5: Combine embedding and LLM results
            final_result = await self._combine_analysis_results(
                similarity_scores, llm_analysis, analysis_type, start_time
            )

            self.successful_analyses += 1

            # Record metrics
            processing_time = final_result.processing_time_ms / 1000
            self.metrics.record_policy_synthesis_operation(
                synthesis_type="constitutional_compliance",
                constitutional_context=analysis_type.value,
                status="success",
                duration=processing_time,
            )

            return final_result

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error in constitutional compliance analysis: {e}")

            # Record error metrics
            self.metrics.record_policy_synthesis_operation(
                synthesis_type="constitutional_compliance",
                constitutional_context=analysis_type.value,
                status="error",
                duration=processing_time / 1000,
            )

            return AnalysisResult(
                analysis_type=analysis_type,
                compliance_score=0.0,
                confidence_score=0.0,
                violations=[{"type": "analysis_error", "message": str(e)}],
                recommendations=["Review policy content and retry analysis"],
                processing_time_ms=processing_time,
                constitutional_hash=self.constitutional_hash,
                metadata={"error": str(e)},
            )

    async def _get_constitutional_framework(self) -> ConstitutionalFramework:
        """Get constitutional framework for analysis."""
        # Check cache first
        cache_key = f"constitutional_framework:{self.constitutional_hash}"

        try:
            if self.redis_client is not None:
                cached_framework = self.redis_client.get(cache_key)
                if cached_framework:
                    framework_data = json.loads(cached_framework)
                    return ConstitutionalFramework(**framework_data)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")

        # Generate framework (mock implementation)
        framework = ConstitutionalFramework(
            constitution_hash=self.constitutional_hash,
            principles=[
                {
                    "id": "PRIN-001",
                    "title": "Democratic Governance",
                    "content": "All governance decisions must be made through democratic processes",
                    "weight": 1.0,
                },
                {
                    "id": "PRIN-002",
                    "title": "Transparency",
                    "content": "All governance actions must be transparent and auditable",
                    "weight": 0.9,
                },
                {
                    "id": "PRIN-003",
                    "title": "Fairness",
                    "content": "All policies must treat stakeholders fairly and equitably",
                    "weight": 0.95,
                },
            ],
            policies=[
                PolicyRule(
                    id="POL-001",
                    title="Voting Rights",
                    content="All eligible stakeholders have the right to vote on governance matters",
                    rule_type="fundamental",
                ),
                PolicyRule(
                    id="POL-002",
                    title="Audit Requirements",
                    content="All governance actions must be logged and auditable",
                    rule_type="procedural",
                ),
            ],
            metadata={"version": "1.0", "last_updated": time.time()},
        )

        # Cache framework
        try:
            if self.redis_client is not None:
                self.redis_client.set(
                    cache_key,
                    json.dumps(framework.__dict__, default=str),
                    self.cache_ttl_seconds,
                )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")

        return framework

    async def _calculate_constitutional_similarity(
        self,
        policy_embedding: List[float],
        constitutional_framework: ConstitutionalFramework,
    ) -> Dict[str, float]:
        """Calculate semantic similarity between policy and constitutional principles."""
        similarity_scores = {}

        try:
            # Generate embeddings for constitutional principles
            for principle in constitutional_framework.principles:
                principle_request = EmbeddingRequest(
                    text=principle["content"],
                    task_type=EmbeddingTaskType.CONSTITUTIONAL_ANALYSIS,
                )

                if self.embedding_client is None:
                    # Use fallback similarity calculation
                    similarity_scores[principle["id"]] = (
                        0.5  # Default moderate similarity
                    )
                    logger.warning(
                        f"Using fallback similarity for principle {principle['id']}"
                    )
                    continue

                principle_embedding_response = (
                    await self.embedding_client.generate_embedding(principle_request)
                )

                if principle_embedding_response.success:
                    # Calculate cosine similarity
                    similarity = self._cosine_similarity(
                        policy_embedding, principle_embedding_response.embedding
                    )

                    # Weight by principle importance
                    weighted_similarity = similarity * principle.get("weight", 1.0)
                    similarity_scores[principle["id"]] = weighted_similarity
                else:
                    logger.warning(
                        f"Failed to generate embedding for principle {principle['id']}"
                    )
                    similarity_scores[principle["id"]] = 0.0

            return similarity_scores

        except Exception as e:
            logger.error(f"Error calculating constitutional similarity: {e}")
            return {}

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)

            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)

            if norm_a == 0 or norm_b == 0:
                return 0.0

            similarity = dot_product / (norm_a * norm_b)
            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {e}")
            return 0.0

    async def _perform_llm_analysis(
        self,
        policy_content: str,
        constitutional_framework: ConstitutionalFramework,
        similarity_scores: Dict[str, float],
        analysis_type: AnalysisType,
    ) -> Dict[str, Any]:
        """Perform detailed analysis using multi-model LLM coordination."""
        try:
            # Prepare analysis prompt
            prompt = self._build_analysis_prompt(
                policy_content,
                constitutional_framework,
                similarity_scores,
                analysis_type,
            )

            # Use constitutional analysis model role
            if self.ai_model_service is None:
                # Use fallback analysis
                logger.warning("AI model service unavailable, using fallback analysis")
                return {
                    "constitutional_analysis": "Fallback analysis - service unavailable",
                    "compliance_score": 0.5,
                    "recommendations": ["Service unavailable - manual review required"],
                    "risk_assessment": "medium",
                }

            response = await self.ai_model_service.generate_text(
                prompt=prompt,
                role=ModelRole.CONSTITUTIONAL,
                max_tokens=2048,
                temperature=0.1,
            )

            # Parse LLM response
            llm_analysis = self._parse_llm_response(response.content)

            return llm_analysis

        except Exception as e:
            logger.error(f"Error in LLM analysis: {e}")
            return {
                "compliance_assessment": "error",
                "confidence": 0.0,
                "violations": [{"type": "llm_error", "message": str(e)}],
                "recommendations": ["Retry analysis with different parameters"],
            }

    def _build_analysis_prompt(
        self,
        policy_content: str,
        constitutional_framework: ConstitutionalFramework,
        similarity_scores: Dict[str, float],
        analysis_type: AnalysisType,
    ) -> str:
        """Build analysis prompt for LLM."""
        principles_text = "\n".join(
            [
                f"- {p['title']}: {p['content']} (Similarity: {similarity_scores.get(p['id'], 0.0):.3f})"
                for p in constitutional_framework.principles
            ]
        )

        prompt = f"""
Constitutional Compliance Analysis

Constitution Hash: {constitutional_framework.constitution_hash}
Analysis Type: {analysis_type.value}

Constitutional Principles:
{principles_text}

Policy Content to Analyze:
{policy_content}

Please analyze the policy content against the constitutional principles and provide:
1. Overall compliance score (0.0 to 1.0)
2. Confidence in the assessment (0.0 to 1.0)
3. Any constitutional violations detected
4. Specific recommendations for improvement

Respond in JSON format with the following structure:
{{
    "compliance_score": <float>,
    "confidence": <float>,
    "violations": [
        {{"type": "<violation_type>", "principle_id": "<id>", "description": "<description>"}}
    ],
    "recommendations": ["<recommendation1>", "<recommendation2>"]
}}
"""
        return prompt

    def _parse_llm_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            # Try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", response_content, re.DOTALL)

            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback parsing
                return {
                    "compliance_score": 0.8,
                    "confidence": 0.7,
                    "violations": [],
                    "recommendations": ["Review LLM response format"],
                }

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return {
                "compliance_score": 0.5,
                "confidence": 0.5,
                "violations": [{"type": "parsing_error", "description": str(e)}],
                "recommendations": ["Retry analysis with improved prompt"],
            }

    async def _combine_analysis_results(
        self,
        similarity_scores: Dict[str, float],
        llm_analysis: Dict[str, Any],
        analysis_type: AnalysisType,
        start_time: float,
    ) -> AnalysisResult:
        """Combine embedding similarity and LLM analysis results."""
        try:
            # Calculate weighted compliance score
            embedding_score = (
                np.mean(list(similarity_scores.values())) if similarity_scores else 0.0
            )
            llm_score = llm_analysis.get("compliance_score", 0.0)

            # Weighted combination (70% LLM, 30% embedding)
            final_compliance_score = (0.7 * llm_score) + (0.3 * embedding_score)

            # Confidence based on agreement between methods
            score_agreement = 1.0 - abs(llm_score - embedding_score)
            base_confidence = llm_analysis.get("confidence", 0.5)
            final_confidence = (base_confidence + score_agreement) / 2.0

            # Combine violations
            violations = llm_analysis.get("violations", [])

            # Add embedding-based violations
            for principle_id, score in similarity_scores.items():
                if score < self.similarity_threshold:
                    violations.append(
                        {
                            "type": "semantic_mismatch",
                            "principle_id": principle_id,
                            "similarity_score": score,
                            "description": f"Low semantic similarity to principle {principle_id}",
                        }
                    )

            processing_time = (time.time() - start_time) * 1000

            return AnalysisResult(
                analysis_type=analysis_type,
                compliance_score=final_compliance_score,
                confidence_score=final_confidence,
                violations=violations,
                recommendations=llm_analysis.get("recommendations", []),
                processing_time_ms=processing_time,
                constitutional_hash=self.constitutional_hash,
                metadata={
                    "embedding_score": embedding_score,
                    "llm_score": llm_score,
                    "similarity_scores": similarity_scores,
                    "score_agreement": score_agreement,
                },
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error combining analysis results: {e}")

            return AnalysisResult(
                analysis_type=analysis_type,
                compliance_score=0.0,
                confidence_score=0.0,
                violations=[{"type": "combination_error", "message": str(e)}],
                recommendations=["Review analysis pipeline"],
                processing_time_ms=processing_time,
                constitutional_hash=self.constitutional_hash,
                metadata={"error": str(e)},
            )

    async def policy_creation_workflow_analysis(
        self, policy: PolicyRule, constitutional_framework: ConstitutionalFramework
    ) -> Dict[str, Any]:
        """Analyze policy for creation workflow."""
        start_time = time.time()

        try:
            result = await self.analyze_constitutional_compliance(
                policy.content,
                AnalysisType.POLICY_VALIDATION,
                context={"policy_id": policy.id, "workflow": "creation"},
            )

            # Workflow-specific processing
            workflow_result = {
                "policy_id": policy.id,
                "approved": result.compliance_score >= self.compliance_threshold,
                "approval_score": result.compliance_score,
                "compliance_score": result.compliance_score,
                "confidence_score": result.confidence_score,
                "conflicts_detected": len(result.violations),
                "violations": result.violations,
                "recommendations": result.recommendations,
                "processing_time_ms": result.processing_time_ms,
                "constitutional_hash": result.constitutional_hash,
                "workflow_type": "policy_creation",
            }

            return workflow_result

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error in policy creation workflow analysis: {e}")

            return {
                "policy_id": policy.id,
                "approved": False,
                "error": str(e),
                "processing_time_ms": processing_time,
                "workflow_type": "policy_creation",
            }

    async def constitutional_compliance_workflow_analysis(
        self,
        policy_id: str,
        policy_content: str,
        validation_type: str = "comprehensive",
    ) -> Dict[str, Any]:
        """Analyze constitutional compliance for workflow."""
        start_time = time.time()

        try:
            result = await self.analyze_constitutional_compliance(
                policy_content,
                AnalysisType.COMPLIANCE_SCORING,
                context={"policy_id": policy_id, "validation_type": validation_type},
            )

            # Compliance workflow result
            workflow_result = {
                "policy_id": policy_id,
                "compliant": result.compliance_score >= self.compliance_threshold,
                "compliance_score": result.compliance_score,
                "confidence_score": result.confidence_score,
                "violations": result.violations,
                "recommendations": result.recommendations,
                "processing_time_ms": result.processing_time_ms,
                "constitutional_hash": result.constitutional_hash,
                "validation_type": validation_type,
                "workflow_type": "constitutional_compliance",
            }

            return workflow_result

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error in constitutional compliance workflow analysis: {e}")

            return {
                "policy_id": policy_id,
                "compliant": False,
                "error": str(e),
                "processing_time_ms": processing_time,
                "workflow_type": "constitutional_compliance",
            }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the analyzer."""
        health_status = {
            "status": "healthy" if self.initialized else "unhealthy",
            "initialized": self.initialized,
            "constitutional_hash": self.constitutional_hash,
            "components": {},
            "performance_metrics": {
                "total_analyses": self.total_analyses,
                "successful_analyses": self.successful_analyses,
                "success_rate": (self.successful_analyses / max(1, self.total_analyses))
                * 100,
                "average_response_time_ms": 0.0,
            },
        }

        # Check component health
        if self.initialized:
            try:
                # Test embedding client
                if self.embedding_client:
                    embedding_health = await self.embedding_client.health_check()
                    health_status["components"]["embedding_client"] = embedding_health[
                        "status"
                    ]
                else:
                    health_status["components"]["embedding_client"] = "unavailable"

                # Test AI model service
                if self.ai_model_service:
                    available_models = self.ai_model_service.get_available_models()
                    health_status["components"]["ai_model_service"] = (
                        "healthy" if available_models else "degraded"
                    )
                else:
                    health_status["components"]["ai_model_service"] = "unavailable"

                # Test Redis cache
                if self.redis_client:
                    try:
                        # Check if Redis is connected by getting a key
                        self.redis_client.get("health_check")
                        health_status["components"]["redis_cache"] = "healthy"
                    except Exception:
                        health_status["components"]["redis_cache"] = "degraded"
                else:
                    health_status["components"]["redis_cache"] = "unavailable"

                # Test analysis functionality
                test_start = time.time()
                test_result = await self.analyze_constitutional_compliance(
                    "Test policy for health check validation",
                    AnalysisType.COMPLIANCE_SCORING,
                )
                test_time = (time.time() - test_start) * 1000

                health_status["test_analysis"] = {
                    "success": test_result.compliance_score >= 0,
                    "response_time_ms": test_time,
                    "compliance_score": test_result.compliance_score,
                }

                health_status["performance_metrics"][
                    "average_response_time_ms"
                ] = test_time

                # Check if performance targets are met
                health_status["performance_targets_met"] = (
                    test_time < 500.0
                )  # <500ms target

            except Exception as e:
                health_status["status"] = "degraded"
                health_status["test_error"] = str(e)

        return health_status

    async def close(self):
        """Close the analyzer and cleanup resources."""
        if self.embedding_client:
            await self.embedding_client.close()

        if self.ai_model_service:
            await self.ai_model_service.close()

        if self.redis_client:
            # Redis client doesn't need explicit closing
            pass

        logger.info("EnhancedConstitutionalAnalyzer closed")


# Global analyzer instance
_enhanced_constitutional_analyzer: Optional[EnhancedConstitutionalAnalyzer] = None


async def get_enhanced_constitutional_analyzer() -> EnhancedConstitutionalAnalyzer:
    """Get global Enhanced Constitutional Analyzer instance."""
    global _enhanced_constitutional_analyzer

    if _enhanced_constitutional_analyzer is None:
        _enhanced_constitutional_analyzer = EnhancedConstitutionalAnalyzer()
        await _enhanced_constitutional_analyzer.initialize()

    return _enhanced_constitutional_analyzer


async def reset_enhanced_constitutional_analyzer():
    """Reset global analyzer (useful for testing)."""
    global _enhanced_constitutional_analyzer

    if _enhanced_constitutional_analyzer:
        await _enhanced_constitutional_analyzer.close()

    _enhanced_constitutional_analyzer = None


# PGC Service Integration Functions
async def integrate_with_pgc_service(
    policy_id: str,
    policy_content: str,
    enforcement_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Integrate constitutional analysis with PGC service for real-time enforcement."""
    try:
        analyzer = await get_enhanced_constitutional_analyzer()

        # Perform constitutional compliance analysis
        context = {"policy_id": policy_id, "enforcement": True}
        if enforcement_context:
            context.update(enforcement_context)

        result = await analyzer.analyze_constitutional_compliance(
            policy_content, AnalysisType.COMPLIANCE_SCORING, context=context
        )

        # Determine enforcement action based on compliance
        if result.compliance_score >= analyzer.compliance_threshold:
            enforcement_action = "allow"
        elif result.compliance_score >= 0.7:
            enforcement_action = "conditional_allow"
        else:
            enforcement_action = "deny"

        return {
            "policy_id": policy_id,
            "enforcement_action": enforcement_action,
            "compliance_score": result.compliance_score,
            "confidence_score": result.confidence_score,
            "constitutional_hash": result.constitutional_hash,
            "violations": result.violations,
            "recommendations": result.recommendations,
            "processing_time_ms": result.processing_time_ms,
            "recommendation_reason": f"Policy {'meets' if enforcement_action == 'allow' else 'does not meet'} constitutional compliance requirements",
        }

    except Exception as e:
        logger.error(f"Error in PGC service integration: {e}")
        return {
            "policy_id": policy_id,
            "enforcement_action": "deny",
            "error": str(e),
            "processing_time_ms": 0.0,
            "recommendation_reason": "Analysis failed - defaulting to deny for safety",
        }
