#!/usr/bin/env python3
"""
Multi-Model Manager for ACGS-1 Constitutional Governance System

This module coordinates between embedding-based analysis and LLM models,
maintaining current model configurations while adding embedding analysis
as an additional layer for comprehensive constitutional governance.

Key Features:
- Coordinates Qwen3 embeddings with existing LLM models
- Maintains current model configurations (Qwen3-32B via Groq, DeepSeek Chat v3, DeepSeek R1)
- Implements consensus mechanism between embedding and LLM results
- Provides unified interface for constitutional analysis
- Supports OpenRouter API integration with extra headers
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json

# ACGS-1 imports
try:
    from .enhanced_constitutional_analyzer import get_enhanced_constitutional_analyzer, AnalysisType
    from .ai_model_service import get_ai_model_service, ModelRole
    from .langgraph_config import get_langgraph_config, ModelRole as LangGraphModelRole
    from .constitutional_metrics import get_constitutional_metrics
    from .redis_cache import get_cache
except ImportError:
    # Fallback for testing
    from enhanced_constitutional_analyzer import get_enhanced_constitutional_analyzer, AnalysisType
    from ai_model_service import get_ai_model_service, ModelRole
    from langgraph_config import get_langgraph_config, ModelRole as LangGraphModelRole
    from constitutional_metrics import get_constitutional_metrics
    from redis_cache import get_cache

logger = logging.getLogger(__name__)


class ConsensusStrategy(str, Enum):
    """Strategies for combining multiple model results."""
    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_VOTE = "majority_vote"
    CONFIDENCE_BASED = "confidence_based"
    EMBEDDING_PRIORITY = "embedding_priority"
    LLM_PRIORITY = "llm_priority"


@dataclass
class ModelResult:
    """Result from a single model analysis."""
    model_id: str
    model_type: str  # "embedding", "llm"
    compliance_score: float
    confidence_score: float
    processing_time_ms: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ConsensusResult:
    """Result from multi-model consensus analysis."""
    final_compliance_score: float
    final_confidence_score: float
    consensus_strategy: ConsensusStrategy
    model_results: List[ModelResult]
    agreement_score: float
    processing_time_ms: float
    recommendations: List[str]
    metadata: Optional[Dict[str, Any]] = None


class MultiModelManager:
    """
    Multi-Model Manager for coordinating embedding and LLM analysis.
    
    Coordinates between Qwen3 embeddings and existing LLM models to provide
    comprehensive constitutional analysis with consensus mechanisms.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Multi-Model Manager."""
        self.config = config or {}
        self.langgraph_config = get_langgraph_config()
        
        # Component references
        self.constitutional_analyzer = None
        self.ai_model_service = None
        self.redis_client = None
        self.metrics = get_constitutional_metrics("multi_model_manager")
        
        # Enhanced Phase 2 model configurations with additional models
        self.model_weights = self.config.get("model_weights", {
            "embedding": 0.25,  # 25% weight for embedding analysis
            "qwen3_32b": 0.20,  # 20% weight for Qwen3-32B (Groq)
            "qwen3_235b": 0.25,  # 25% weight for Qwen3-235B (OpenRouter)
            "deepseek_chat_v3": 0.20,  # 20% weight for DeepSeek Chat v3
            "deepseek_r1": 0.10   # 10% weight for DeepSeek R1 (OpenRouter)
        })

        # Failover configuration for model reliability
        self.failover_config = self.config.get("failover_config", {
            "max_retries": 3,
            "timeout_seconds": 30.0,
            "fallback_threshold": 0.5,  # Minimum confidence for accepting results
            "consensus_threshold": 0.7   # Minimum agreement for high confidence
        })

        # Phase 2 enhanced model configurations
        self.enhanced_models = {
            "qwen3_235b": {
                "provider": "openrouter",
                "model_id": "qwen/qwen3-235b-a22b:free",
                "role": "constitutional_analysis",
                "max_tokens": 4096,
                "temperature": 0.1,
            },
            "deepseek_r1": {
                "provider": "openrouter",
                "model_id": "deepseek/deepseek-r1",
                "role": "reasoning_validation",
                "max_tokens": 8192,
                "temperature": 0.0,
            },
            "deepseek_chat_v3_enhanced": {
                "provider": "direct",
                "model_id": "deepseek-chat-v3-0324",
                "role": "policy_synthesis",
                "max_tokens": 4096,
                "temperature": 0.2,
            }
        }
        
        # Consensus settings
        self.default_consensus_strategy = ConsensusStrategy(
            self.config.get("consensus_strategy", "weighted_average")
        )
        self.agreement_threshold = self.config.get("agreement_threshold", 0.8)
        self.cache_ttl_seconds = self.config.get("cache_ttl_seconds", 1800)
        
        # State tracking
        self.initialized = False
        self.total_analyses = 0
        self.successful_analyses = 0
        
        logger.info("MultiModelManager initialized")

    async def initialize(self) -> bool:
        """Initialize the multi-model manager and its components."""
        try:
            start_time = time.time()
            
            # Initialize constitutional analyzer (includes embedding client)
            self.constitutional_analyzer = await get_enhanced_constitutional_analyzer()
            
            # Initialize AI model service
            self.ai_model_service = await get_ai_model_service()
            
            # Initialize Redis cache
            self.redis_client = get_cache()
            
            self.initialized = True
            
            init_time = (time.time() - start_time) * 1000
            logger.info(f"MultiModelManager initialized successfully in {init_time:.2f}ms")
            
            # Record initialization metrics
            self.metrics.record_constitutional_principle_operation(
                operation_type="manager_initialization",
                principle_category="multi_model_coordination",
                status="success"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MultiModelManager: {e}")
            self.metrics.record_constitutional_principle_operation(
                operation_type="manager_initialization",
                principle_category="multi_model_coordination",
                status="error"
            )
            return False

    async def analyze_with_consensus(
        self,
        policy_content: str,
        analysis_type: AnalysisType = AnalysisType.COMPLIANCE_SCORING,
        consensus_strategy: Optional[ConsensusStrategy] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ConsensusResult:
        """
        Perform constitutional analysis using multiple models with consensus.
        
        Args:
            policy_content: Policy content to analyze
            analysis_type: Type of analysis to perform
            consensus_strategy: Strategy for combining results
            context: Additional context for analysis
            
        Returns:
            ConsensusResult with consensus analysis and model coordination
        """
        start_time = time.time()
        self.total_analyses += 1
        
        try:
            # Use default consensus strategy if not specified
            strategy = consensus_strategy or self.default_consensus_strategy
            
            # Check cache first
            cache_key = self._generate_cache_key(policy_content, analysis_type, strategy)
            cached_result = await self._get_cached_result(cache_key)
            if cached_result:
                return cached_result
            
            # Step 1: Get embedding-based analysis
            embedding_result = await self._get_embedding_analysis(
                policy_content, analysis_type, context
            )
            
            # Step 2: Get LLM-based analyses
            llm_results = await self._get_llm_analyses(
                policy_content, analysis_type, context
            )
            
            # Step 3: Combine results using consensus strategy
            consensus_result = await self._apply_consensus_strategy(
                embedding_result,
                llm_results,
                strategy,
                start_time
            )
            
            # Cache result
            await self._cache_result(cache_key, consensus_result)
            
            self.successful_analyses += 1
            
            # Record metrics
            processing_time = consensus_result.processing_time_ms / 1000
            self.metrics.record_policy_synthesis_operation(
                synthesis_type="multi_model_consensus",
                constitutional_context=analysis_type.value,
                status="success",
                duration=processing_time
            )
            
            return consensus_result
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error in multi-model consensus analysis: {e}")
            
            # Record error metrics
            self.metrics.record_policy_synthesis_operation(
                synthesis_type="multi_model_consensus",
                constitutional_context=analysis_type.value,
                status="error",
                duration=processing_time / 1000
            )
            
            return ConsensusResult(
                final_compliance_score=0.0,
                final_confidence_score=0.0,
                consensus_strategy=strategy,
                model_results=[],
                agreement_score=0.0,
                processing_time_ms=processing_time,
                recommendations=["Multi-model analysis failed - review system configuration"],
                metadata={"error": str(e)}
            )

    async def _get_embedding_analysis(
        self,
        policy_content: str,
        analysis_type: AnalysisType,
        context: Optional[Dict[str, Any]]
    ) -> ModelResult:
        """Get analysis from embedding-based constitutional analyzer."""
        try:
            start_time = time.time()
            
            result = await self.constitutional_analyzer.analyze_constitutional_compliance(
                policy_content, analysis_type, context
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return ModelResult(
                model_id="enhanced_constitutional_analyzer",
                model_type="embedding",
                compliance_score=result.compliance_score,
                confidence_score=result.confidence_score,
                processing_time_ms=processing_time,
                metadata={
                    "violations": result.violations,
                    "recommendations": result.recommendations,
                    "constitutional_hash": result.constitutional_hash
                }
            )
            
        except Exception as e:
            logger.error(f"Error in embedding analysis: {e}")
            return ModelResult(
                model_id="enhanced_constitutional_analyzer",
                model_type="embedding",
                compliance_score=0.0,
                confidence_score=0.0,
                processing_time_ms=0.0,
                metadata={"error": str(e)}
            )

    async def _get_llm_analyses(
        self,
        policy_content: str,
        analysis_type: AnalysisType,
        context: Optional[Dict[str, Any]]
    ) -> List[ModelResult]:
        """Get analyses from multiple LLM models."""
        llm_results = []
        
        # Enhanced model configurations for constitutional analysis with 4+ models
        llm_models = [
            {
                "role": LangGraphModelRole.CONSTITUTIONAL_PROMPTING,
                "model_id": "qwen3_235b_openrouter",
                "weight": self.model_weights.get("qwen3_235b", 0.25)
            },
            {
                "role": LangGraphModelRole.POLICY_SYNTHESIS,
                "model_id": "deepseek_chat_v3_openrouter",
                "weight": self.model_weights.get("deepseek_chat_v3", 0.20)
            },
            {
                "role": LangGraphModelRole.REFLECTION,
                "model_id": "deepseek_r1_openrouter_enhanced",
                "weight": self.model_weights.get("deepseek_r1", 0.10)
            },
            {
                "role": LangGraphModelRole.CONSTITUTIONAL_PROMPTING,
                "model_id": "qwen3_32b_groq",
                "weight": self.model_weights.get("qwen3_32b", 0.20)
            }
        ]
        
        # Run LLM analyses in parallel
        tasks = []
        for model_config in llm_models:
            task = self._get_single_llm_analysis(
                policy_content, analysis_type, context, model_config
            )
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, ModelResult):
                    llm_results.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"LLM analysis failed: {result}")
                    
        except Exception as e:
            logger.error(f"Error in parallel LLM analyses: {e}")
        
        return llm_results

    async def _get_single_llm_analysis(
        self,
        policy_content: str,
        analysis_type: AnalysisType,
        context: Optional[Dict[str, Any]],
        model_config: Dict[str, Any]
    ) -> ModelResult:
        """Get analysis from a single LLM model."""
        try:
            start_time = time.time()

            # Build constitutional analysis prompt
            prompt = self._build_llm_prompt(policy_content, analysis_type, context)

            # Generate response using specified model role
            response = await self.ai_model_service.generate_text(
                prompt=prompt,
                role=model_config["role"],
                max_tokens=1024,
                temperature=0.1
            )

            # Parse response for compliance scoring
            compliance_score, confidence_score = self._parse_llm_compliance_response(response.content)

            processing_time = (time.time() - start_time) * 1000

            return ModelResult(
                model_id=model_config["model_id"],
                model_type="llm",
                compliance_score=compliance_score,
                confidence_score=confidence_score,
                processing_time_ms=processing_time,
                metadata={
                    "model_role": model_config["role"].value,
                    "response_content": response.content[:500],  # Truncated for storage
                    "weight": model_config["weight"]
                }
            )

        except Exception as e:
            logger.error(f"Error in single LLM analysis for {model_config['model_id']}: {e}")
            return ModelResult(
                model_id=model_config["model_id"],
                model_type="llm",
                compliance_score=0.0,
                confidence_score=0.0,
                processing_time_ms=0.0,
                metadata={"error": str(e), "weight": model_config.get("weight", 0.0)}
            )

    def _build_llm_prompt(
        self,
        policy_content: str,
        analysis_type: AnalysisType,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for LLM constitutional analysis."""
        context_str = ""
        if context:
            context_str = f"\nContext: {json.dumps(context, indent=2)}"

        prompt = f"""
Constitutional Compliance Analysis

Analysis Type: {analysis_type.value}
Constitution Hash: cdd01ef066bc6cf2

Policy Content:
{policy_content}
{context_str}

Please analyze this policy content for constitutional compliance and provide:
1. A compliance score from 0.0 to 1.0 (where 1.0 is fully compliant)
2. A confidence score from 0.0 to 1.0 (how confident you are in the assessment)
3. Brief reasoning for the scores

Respond in this format:
COMPLIANCE_SCORE: <score>
CONFIDENCE_SCORE: <score>
REASONING: <brief explanation>
"""
        return prompt

    def _parse_llm_compliance_response(self, response_content: str) -> tuple[float, float]:
        """Parse LLM response to extract compliance and confidence scores."""
        try:
            import re

            # Extract compliance score
            compliance_match = re.search(r'COMPLIANCE_SCORE:\s*([0-9.]+)', response_content)
            compliance_score = float(compliance_match.group(1)) if compliance_match else 0.5

            # Extract confidence score
            confidence_match = re.search(r'CONFIDENCE_SCORE:\s*([0-9.]+)', response_content)
            confidence_score = float(confidence_match.group(1)) if confidence_match else 0.5

            # Ensure scores are in valid range
            compliance_score = max(0.0, min(1.0, compliance_score))
            confidence_score = max(0.0, min(1.0, confidence_score))

            return compliance_score, confidence_score

        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return 0.5, 0.5  # Default scores

    async def _apply_consensus_strategy(
        self,
        embedding_result: ModelResult,
        llm_results: List[ModelResult],
        strategy: ConsensusStrategy,
        start_time: float
    ) -> ConsensusResult:
        """Apply consensus strategy to combine model results."""
        try:
            all_results = [embedding_result] + llm_results

            if strategy == ConsensusStrategy.WEIGHTED_AVERAGE:
                final_score, final_confidence = self._weighted_average_consensus(all_results)
            elif strategy == ConsensusStrategy.CONFIDENCE_BASED:
                final_score, final_confidence = self._confidence_based_consensus(all_results)
            elif strategy == ConsensusStrategy.EMBEDDING_PRIORITY:
                final_score, final_confidence = self._embedding_priority_consensus(embedding_result, llm_results)
            else:
                # Default to weighted average
                final_score, final_confidence = self._weighted_average_consensus(all_results)

            # Calculate agreement score
            agreement_score = self._calculate_agreement_score(all_results)

            # Generate recommendations
            recommendations = self._generate_consensus_recommendations(all_results, agreement_score)

            processing_time = (time.time() - start_time) * 1000

            return ConsensusResult(
                final_compliance_score=final_score,
                final_confidence_score=final_confidence,
                consensus_strategy=strategy,
                model_results=all_results,
                agreement_score=agreement_score,
                processing_time_ms=processing_time,
                recommendations=recommendations,
                metadata={
                    "embedding_weight": self.model_weights.get("embedding", 0.4),
                    "total_models": len(all_results),
                    "successful_models": len([r for r in all_results if r.compliance_score > 0])
                }
            )

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error applying consensus strategy: {e}")

            return ConsensusResult(
                final_compliance_score=0.0,
                final_confidence_score=0.0,
                consensus_strategy=strategy,
                model_results=all_results,
                agreement_score=0.0,
                processing_time_ms=processing_time,
                recommendations=["Consensus strategy failed - review model coordination"],
                metadata={"error": str(e)}
            )

    def _weighted_average_consensus(self, results: List[ModelResult]) -> tuple[float, float]:
        """Calculate enhanced weighted average consensus with improved model recognition."""
        total_weight = 0.0
        weighted_compliance = 0.0
        weighted_confidence = 0.0

        for result in results:
            # Enhanced model weight determination
            weight = self._get_model_weight(result)

            # Apply confidence-based weight adjustment for better consensus
            confidence_multiplier = min(1.0, result.confidence_score + 0.5)
            adjusted_weight = weight * confidence_multiplier

            if result.compliance_score > 0:  # Only include successful results
                weighted_compliance += result.compliance_score * adjusted_weight
                weighted_confidence += result.confidence_score * adjusted_weight
                total_weight += adjusted_weight

        if total_weight > 0:
            final_compliance = weighted_compliance / total_weight
            final_confidence = weighted_confidence / total_weight

            # Apply consensus threshold check
            if final_confidence < self.failover_config.get("fallback_threshold", 0.5):
                logger.warning(f"Low consensus confidence: {final_confidence:.3f}")
        else:
            final_compliance = 0.0
            final_confidence = 0.0

        return final_compliance, final_confidence

    def _get_model_weight(self, result: ModelResult) -> float:
        """Get model weight based on model type and ID with enhanced recognition."""
        if result.model_type == "embedding":
            return self.model_weights.get("embedding", 0.25)

        # Enhanced model ID recognition for OpenRouter models
        model_id_lower = result.model_id.lower()

        if "qwen3_235b" in model_id_lower or "qwen3-235b" in model_id_lower:
            return self.model_weights.get("qwen3_235b", 0.25)
        elif "qwen3_32b" in model_id_lower or "qwen3-32b" in model_id_lower:
            return self.model_weights.get("qwen3_32b", 0.20)
        elif "deepseek_chat_v3" in model_id_lower or "deepseek-chat-v3" in model_id_lower:
            return self.model_weights.get("deepseek_chat_v3", 0.20)
        elif "deepseek_r1" in model_id_lower or "deepseek-r1" in model_id_lower:
            return self.model_weights.get("deepseek_r1", 0.10)
        else:
            # Use metadata weight if available, otherwise default
            return result.metadata.get("weight", 0.05) if result.metadata else 0.05

    def _confidence_based_consensus(self, results: List[ModelResult]) -> tuple[float, float]:
        """Calculate confidence-based consensus."""
        if not results:
            return 0.0, 0.0

        # Weight by confidence scores
        total_confidence = sum(r.confidence_score for r in results if r.compliance_score > 0)

        if total_confidence > 0:
            weighted_compliance = sum(
                r.compliance_score * r.confidence_score
                for r in results if r.compliance_score > 0
            ) / total_confidence

            avg_confidence = total_confidence / len([r for r in results if r.compliance_score > 0])
        else:
            weighted_compliance = 0.0
            avg_confidence = 0.0

        return weighted_compliance, avg_confidence

    def _embedding_priority_consensus(
        self,
        embedding_result: ModelResult,
        llm_results: List[ModelResult]
    ) -> tuple[float, float]:
        """Calculate embedding-priority consensus."""
        # Give 70% weight to embedding, 30% to LLM average
        embedding_weight = 0.7
        llm_weight = 0.3

        # Calculate LLM average
        valid_llm_results = [r for r in llm_results if r.compliance_score > 0]
        if valid_llm_results:
            llm_avg_compliance = sum(r.compliance_score for r in valid_llm_results) / len(valid_llm_results)
            llm_avg_confidence = sum(r.confidence_score for r in valid_llm_results) / len(valid_llm_results)
        else:
            llm_avg_compliance = 0.0
            llm_avg_confidence = 0.0

        # Combine with embedding priority
        final_compliance = (
            embedding_result.compliance_score * embedding_weight +
            llm_avg_compliance * llm_weight
        )
        final_confidence = (
            embedding_result.confidence_score * embedding_weight +
            llm_avg_confidence * llm_weight
        )

        return final_compliance, final_confidence

    def _calculate_agreement_score(self, results: List[ModelResult]) -> float:
        """Calculate agreement score between models."""
        if len(results) < 2:
            return 1.0

        valid_results = [r for r in results if r.compliance_score > 0]
        if len(valid_results) < 2:
            return 0.0

        scores = [r.compliance_score for r in valid_results]
        mean_score = sum(scores) / len(scores)

        # Calculate standard deviation
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5

        # Convert to agreement score (lower std_dev = higher agreement)
        agreement_score = max(0.0, 1.0 - (std_dev * 2))  # Scale factor of 2

        return agreement_score

    def _generate_consensus_recommendations(
        self,
        results: List[ModelResult],
        agreement_score: float
    ) -> List[str]:
        """Generate recommendations based on consensus analysis."""
        recommendations = []

        # Check agreement level
        if agreement_score < self.agreement_threshold:
            recommendations.append(
                f"⚠️ Low model agreement ({agreement_score:.2f}) - consider manual review"
            )

        # Check individual model performance
        failed_models = [r for r in results if r.compliance_score == 0]
        if failed_models:
            model_names = [r.model_id for r in failed_models]
            recommendations.append(
                f"🔧 Model failures detected: {', '.join(model_names)}"
            )

        # Check compliance levels
        compliance_scores = [r.compliance_score for r in results if r.compliance_score > 0]
        if compliance_scores:
            avg_compliance = sum(compliance_scores) / len(compliance_scores)
            if avg_compliance < 0.7:
                recommendations.append(
                    "🚨 Low constitutional compliance detected - policy revision recommended"
                )
            elif avg_compliance < 0.9:
                recommendations.append(
                    "⚠️ Moderate compliance concerns - review constitutional alignment"
                )

        # Performance recommendations
        processing_times = [r.processing_time_ms for r in results if r.processing_time_ms > 0]
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            if avg_time > 1000:  # >1 second
                recommendations.append(
                    "⏱️ High processing time - consider model optimization"
                )

        if not recommendations:
            recommendations.append("✅ Constitutional analysis completed successfully")

        return recommendations

    def _generate_cache_key(
        self,
        policy_content: str,
        analysis_type: AnalysisType,
        strategy: ConsensusStrategy
    ) -> str:
        """Generate cache key for consensus result."""
        import hashlib
        content_hash = hashlib.sha256(policy_content.encode()).hexdigest()[:16]
        return f"multi_model_consensus:{content_hash}:{analysis_type.value}:{strategy.value}"

    async def _get_cached_result(self, cache_key: str) -> Optional[ConsensusResult]:
        """Get cached consensus result if available."""
        if not self.redis_client:
            return None

        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                # Reconstruct ConsensusResult from cached data
                return ConsensusResult(**data)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")

        return None

    async def _cache_result(self, cache_key: str, result: ConsensusResult):
        """Cache consensus result for future use."""
        if not self.redis_client:
            return

        try:
            # Convert to dict for JSON serialization
            result_dict = {
                "final_compliance_score": result.final_compliance_score,
                "final_confidence_score": result.final_confidence_score,
                "consensus_strategy": result.consensus_strategy.value,
                "model_results": [
                    {
                        "model_id": r.model_id,
                        "model_type": r.model_type,
                        "compliance_score": r.compliance_score,
                        "confidence_score": r.confidence_score,
                        "processing_time_ms": r.processing_time_ms,
                        "metadata": r.metadata
                    }
                    for r in result.model_results
                ],
                "agreement_score": result.agreement_score,
                "processing_time_ms": result.processing_time_ms,
                "recommendations": result.recommendations,
                "metadata": result.metadata
            }

            self.redis_client.set(
                cache_key,
                json.dumps(result_dict, default=str),
                self.cache_ttl_seconds
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the multi-model manager."""
        health_status = {
            "status": "healthy" if self.initialized else "unhealthy",
            "initialized": self.initialized,
            "components": {},
            "model_weights": self.model_weights,
            "consensus_strategy": self.default_consensus_strategy.value,
            "performance_metrics": {
                "total_analyses": self.total_analyses,
                "successful_analyses": self.successful_analyses,
                "success_rate": (self.successful_analyses / max(1, self.total_analyses)) * 100,
            },
        }

        # Check component health
        if self.initialized:
            try:
                # Test constitutional analyzer
                if self.constitutional_analyzer:
                    analyzer_health = await self.constitutional_analyzer.health_check()
                    health_status["components"]["constitutional_analyzer"] = analyzer_health["status"]
                else:
                    health_status["components"]["constitutional_analyzer"] = "unavailable"

                # Test AI model service
                if self.ai_model_service:
                    available_models = self.ai_model_service.get_available_models()
                    health_status["components"]["ai_model_service"] = "healthy" if available_models else "degraded"
                    health_status["available_models"] = list(available_models.keys())
                else:
                    health_status["components"]["ai_model_service"] = "unavailable"

                # Test Redis cache
                if self.redis_client:
                    try:
                        # Test cache connectivity by getting a key
                        self.redis_client.get("health_check")
                        health_status["components"]["redis_cache"] = "healthy"
                    except Exception:
                        health_status["components"]["redis_cache"] = "degraded"
                else:
                    health_status["components"]["redis_cache"] = "unavailable"

                # Test consensus functionality
                test_start = time.time()
                test_result = await self.analyze_with_consensus(
                    "Test policy for multi-model health check validation",
                    AnalysisType.COMPLIANCE_SCORING
                )
                test_time = (time.time() - test_start) * 1000

                health_status["test_consensus"] = {
                    "success": test_result.final_compliance_score >= 0,
                    "response_time_ms": test_time,
                    "agreement_score": test_result.agreement_score,
                    "models_used": len(test_result.model_results)
                }

                # Check if performance targets are met
                health_status["performance_targets_met"] = test_time < 500.0  # <500ms target

            except Exception as e:
                health_status["status"] = "degraded"
                health_status["test_error"] = str(e)

        return health_status

    async def close(self):
        """Close the multi-model manager and cleanup resources."""
        if self.constitutional_analyzer:
            await self.constitutional_analyzer.close()

        if self.ai_model_service:
            await self.ai_model_service.close()

        if self.redis_client:
            # Redis client doesn't need explicit closing
            pass

        logger.info("MultiModelManager closed")


# Global manager instance
_multi_model_manager: Optional[MultiModelManager] = None


async def get_multi_model_manager() -> MultiModelManager:
    """Get global Multi-Model Manager instance."""
    global _multi_model_manager

    if _multi_model_manager is None:
        _multi_model_manager = MultiModelManager()
        await _multi_model_manager.initialize()

    return _multi_model_manager


async def reset_multi_model_manager():
    """Reset global manager (useful for testing)."""
    global _multi_model_manager

    if _multi_model_manager:
        await _multi_model_manager.close()

    _multi_model_manager = None
