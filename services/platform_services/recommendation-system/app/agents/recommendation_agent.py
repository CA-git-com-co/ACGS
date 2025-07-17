"""
Recommendation Agent - Orchestrates different recommendation strategies
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import time
from typing import List, Dict, Optional, Any
import asyncio
from datetime import datetime

from ..models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendationItem,
    RecommendationType,
    ContentType,
    UserInteraction,
    PersonalizationMetrics,
    CONSTITUTIONAL_HASH
)
from ..services.vector_service import VectorService
from ..services.collaborative_filtering import CollaborativeFilteringService

logger = logging.getLogger(__name__)

class RecommendationAgent:
    """
    Main recommendation agent that orchestrates different recommendation strategies
    and applies constitutional compliance filtering.
    """
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379/0",
                 vector_redis_url: str = "redis://localhost:6379/1",
                 collab_redis_url: str = "redis://localhost:6379/2"):
        """Initialize recommendation agent with all services."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Initialize services
        self.vector_service = VectorService(vector_redis_url)
        self.collaborative_service = CollaborativeFilteringService(collab_redis_url)
        
        # Strategy weights for hybrid recommendations
        self.strategy_weights = {
            RecommendationType.COLLABORATIVE_FILTERING: 0.4,
            RecommendationType.CONTENT_BASED: 0.3,
            RecommendationType.VECTOR_SIMILARITY: 0.2,
            RecommendationType.CONSTITUTIONAL_ALIGNED: 0.1
        }
        
        # Constitutional compliance thresholds
        self.constitutional_threshold = 0.7
        self.min_constitutional_score = 0.5
        
        logger.info("RecommendationAgent initialized")
    
    async def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Generate recommendations based on the requested strategy.
        
        Args:
            request: Recommendation request with user preferences
            
        Returns:
            RecommendationResponse with personalized recommendations
        """
        start_time = time.time()
        
        try:
            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise ValueError(f"Constitutional hash mismatch: {request.constitutional_hash}")
            
            # Get recommendations based on strategy
            recommendations = []
            
            if request.recommendation_type == RecommendationType.COLLABORATIVE_FILTERING:
                recommendations = await self._get_collaborative_recommendations(request)
            elif request.recommendation_type == RecommendationType.CONTENT_BASED:
                recommendations = await self._get_content_based_recommendations(request)
            elif request.recommendation_type == RecommendationType.VECTOR_SIMILARITY:
                recommendations = await self._get_vector_similarity_recommendations(request)
            elif request.recommendation_type == RecommendationType.HYBRID:
                recommendations = await self._get_hybrid_recommendations(request)
            elif request.recommendation_type == RecommendationType.CONSTITUTIONAL_ALIGNED:
                recommendations = await self._get_constitutional_recommendations(request)
            else:
                # Default to hybrid
                recommendations = await self._get_hybrid_recommendations(request)
            
            # Apply constitutional compliance filtering
            recommendations = await self._apply_constitutional_filtering(
                recommendations, request.constitutional_weight
            )
            
            # Apply content type filtering
            if request.content_types:
                recommendations = [
                    r for r in recommendations 
                    if r.content_type in request.content_types
                ]
            
            # Remove excluded items
            if request.exclude_ids:
                recommendations = [
                    r for r in recommendations 
                    if r.content_id not in request.exclude_ids
                ]
            
            # Limit results
            recommendations = recommendations[:request.limit]
            
            # Calculate personalization score
            personalization_score = await self._calculate_personalization_score(
                request.user_id, recommendations
            )
            
            # Calculate constitutional compliance
            constitutional_compliance = await self._calculate_constitutional_compliance(
                recommendations
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            return RecommendationResponse(
                user_id=request.user_id,
                recommendations=recommendations,
                algorithm_used=request.recommendation_type,
                total_items=len(recommendations),
                personalization_score=personalization_score,
                constitutional_compliance=constitutional_compliance,
                metadata={
                    "processing_time_ms": processing_time,
                    "constitutional_weight": request.constitutional_weight,
                    "strategy_weights": self.strategy_weights
                },
                constitutional_hash=self.constitutional_hash,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return RecommendationResponse(
                user_id=request.user_id,
                recommendations=[],
                algorithm_used=request.recommendation_type,
                total_items=0,
                personalization_score=0.0,
                constitutional_compliance={"error": str(e)},
                constitutional_hash=self.constitutional_hash
            )
    
    async def _get_collaborative_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Get collaborative filtering recommendations."""
        try:
            # Try user-based collaborative filtering first
            user_based = await self.collaborative_service.get_user_based_recommendations(
                request.user_id, request.limit
            )
            
            # If not enough results, try item-based
            if len(user_based) < request.limit:
                item_based = await self.collaborative_service.get_item_based_recommendations(
                    request.user_id, request.limit - len(user_based)
                )
                user_based.extend(item_based)
            
            # Add recommendation type info
            for item in user_based:
                item.reason = f"Collaborative filtering: {item.reason}"
            
            return user_based
            
        except Exception as e:
            logger.error(f"Collaborative recommendations failed: {e}")
            return []
    
    async def _get_content_based_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Get content-based recommendations."""
        try:
            # Get user's interaction history to understand preferences
            user_interactions = await self._get_user_interactions(request.user_id)
            
            if not user_interactions:
                return []
            
            # Get content items user has interacted with
            interacted_content_ids = [i.content_id for i in user_interactions]
            
            # Find similar content for each item
            all_similar = []
            
            for content_id in interacted_content_ids[-10:]:  # Last 10 interactions
                similar_results = await self.vector_service.search_similar_to_content(
                    content_id, limit=5
                )
                all_similar.extend(similar_results)
            
            # Convert to recommendation items
            recommendations = []
            seen_content_ids = set()
            
            for result in all_similar:
                if result.content_id not in seen_content_ids:
                    item = RecommendationItem(
                        content_id=result.content_id,
                        title=result.content.title,
                        description=result.content.description,
                        content_type=result.content.content_type,
                        score=result.combined_score,
                        confidence=result.similarity_score,
                        reason="Content-based: Similar to items you've liked",
                        tags=result.content.tags,
                        metadata=result.content.metadata,
                        constitutional_score=result.constitutional_score
                    )
                    recommendations.append(item)
                    seen_content_ids.add(result.content_id)
            
            return recommendations[:request.limit]
            
        except Exception as e:
            logger.error(f"Content-based recommendations failed: {e}")
            return []
    
    async def _get_vector_similarity_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Get vector similarity recommendations."""
        try:
            # Get user's recent interactions to build query vector
            user_interactions = await self._get_user_interactions(request.user_id)
            
            if not user_interactions:
                return []
            
            # Build user preference vector from interactions
            user_vector = await self._build_user_preference_vector(user_interactions)
            
            if not user_vector:
                return []
            
            # Search for similar content
            from ..models.schemas import SimilaritySearchRequest
            search_request = SimilaritySearchRequest(
                query_vector=user_vector,
                limit=request.limit,
                threshold=0.3,
                constitutional_weight=request.constitutional_weight,
                constitutional_hash=self.constitutional_hash
            )
            
            similar_results = await self.vector_service.search_similar(search_request)
            
            # Convert to recommendation items
            recommendations = []
            for result in similar_results:
                item = RecommendationItem(
                    content_id=result.content_id,
                    title=result.content.title,
                    description=result.content.description,
                    content_type=result.content.content_type,
                    score=result.combined_score,
                    confidence=result.similarity_score,
                    reason="Vector similarity: Matches your interests",
                    tags=result.content.tags,
                    metadata=result.content.metadata,
                    constitutional_score=result.constitutional_score
                )
                recommendations.append(item)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Vector similarity recommendations failed: {e}")
            return []
    
    async def _get_hybrid_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Get hybrid recommendations combining multiple strategies."""
        try:
            # Get recommendations from different strategies
            tasks = [
                self._get_collaborative_recommendations(request),
                self._get_content_based_recommendations(request),
                self._get_vector_similarity_recommendations(request)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results with weights
            all_recommendations = {}
            
            strategies = [
                (RecommendationType.COLLABORATIVE_FILTERING, results[0]),
                (RecommendationType.CONTENT_BASED, results[1]),
                (RecommendationType.VECTOR_SIMILARITY, results[2])
            ]
            
            for strategy, recommendations in strategies:
                if isinstance(recommendations, Exception):
                    logger.error(f"Strategy {strategy} failed: {recommendations}")
                    continue
                
                weight = self.strategy_weights.get(strategy, 0.1)
                
                for item in recommendations:
                    if item.content_id not in all_recommendations:
                        all_recommendations[item.content_id] = {
                            "item": item,
                            "weighted_score": item.score * weight,
                            "strategies": [strategy.value]
                        }
                    else:
                        # Combine scores from multiple strategies
                        all_recommendations[item.content_id]["weighted_score"] += item.score * weight
                        all_recommendations[item.content_id]["strategies"].append(strategy.value)
            
            # Sort by weighted score
            sorted_recommendations = sorted(
                all_recommendations.values(),
                key=lambda x: x["weighted_score"],
                reverse=True
            )
            
            # Build final recommendations
            final_recommendations = []
            for data in sorted_recommendations[:request.limit]:
                item = data["item"]
                item.score = data["weighted_score"]
                item.reason = f"Hybrid ({', '.join(data['strategies'])}): {item.reason}"
                final_recommendations.append(item)
            
            return final_recommendations
            
        except Exception as e:
            logger.error(f"Hybrid recommendations failed: {e}")
            return []
    
    async def _get_constitutional_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Get recommendations prioritizing constitutional compliance."""
        try:
            # Get all recommendations and filter by constitutional score
            hybrid_recommendations = await self._get_hybrid_recommendations(request)
            
            # Filter and re-rank by constitutional compliance
            constitutional_recs = []
            for item in hybrid_recommendations:
                if item.constitutional_score >= self.constitutional_threshold:
                    # Boost score based on constitutional compliance
                    constitutional_boost = item.constitutional_score * 0.5
                    item.score = min(1.0, item.score + constitutional_boost)
                    item.reason = f"Constitutional priority: {item.reason}"
                    constitutional_recs.append(item)
            
            # Sort by constitutional score first, then by original score
            constitutional_recs.sort(
                key=lambda x: (x.constitutional_score, x.score),
                reverse=True
            )
            
            return constitutional_recs
            
        except Exception as e:
            logger.error(f"Constitutional recommendations failed: {e}")
            return []
    
    async def _apply_constitutional_filtering(self, 
                                           recommendations: List[RecommendationItem], 
                                           constitutional_weight: float) -> List[RecommendationItem]:
        """Apply constitutional compliance filtering to recommendations."""
        try:
            filtered_recommendations = []
            
            for item in recommendations:
                # Check minimum constitutional score
                if item.constitutional_score < self.min_constitutional_score:
                    continue
                
                # Apply constitutional weighting to score
                original_score = item.score
                constitutional_score = item.constitutional_score
                
                # Weighted combination
                item.score = (
                    original_score * (1 - constitutional_weight) +
                    constitutional_score * constitutional_weight
                )
                
                filtered_recommendations.append(item)
            
            # Sort by updated scores
            filtered_recommendations.sort(key=lambda x: x.score, reverse=True)
            
            return filtered_recommendations
            
        except Exception as e:
            logger.error(f"Constitutional filtering failed: {e}")
            return recommendations
    
    async def _get_user_interactions(self, user_id: str) -> List[UserInteraction]:
        """Get user interactions for personalization."""
        try:
            # This would integrate with the collaborative filtering service
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Failed to get user interactions: {e}")
            return []
    
    async def _build_user_preference_vector(self, interactions: List[UserInteraction]) -> Optional[List[float]]:
        """Build user preference vector from interactions."""
        try:
            if not interactions:
                return None
            
            # Get content embeddings for interacted items
            content_vectors = []
            weights = []
            
            for interaction in interactions:
                # Get content vector (mock implementation)
                content_vector = [0.1] * 384  # Mock 384-dimensional vector
                
                # Weight by interaction type and rating
                weight = 1.0
                if interaction.rating:
                    weight = interaction.rating / 5.0
                
                content_vectors.append(content_vector)
                weights.append(weight)
            
            if not content_vectors:
                return None
            
            # Calculate weighted average
            import numpy as np
            vectors = np.array(content_vectors)
            weights = np.array(weights)
            
            # Weighted average
            user_vector = np.average(vectors, axis=0, weights=weights)
            
            return user_vector.tolist()
            
        except Exception as e:
            logger.error(f"Failed to build user preference vector: {e}")
            return None
    
    async def _calculate_personalization_score(self, user_id: str, recommendations: List[RecommendationItem]) -> float:
        """Calculate personalization effectiveness score."""
        try:
            if not recommendations:
                return 0.0
            
            # Calculate diversity (variety of content types and topics)
            content_types = set(r.content_type for r in recommendations)
            diversity_score = len(content_types) / len(ContentType)
            
            # Calculate confidence (average confidence of recommendations)
            confidence_score = sum(r.confidence for r in recommendations) / len(recommendations)
            
            # Calculate constitutional alignment
            constitutional_score = sum(r.constitutional_score for r in recommendations) / len(recommendations)
            
            # Combined personalization score
            personalization_score = (
                diversity_score * 0.3 +
                confidence_score * 0.4 +
                constitutional_score * 0.3
            )
            
            return min(1.0, personalization_score)
            
        except Exception as e:
            logger.error(f"Failed to calculate personalization score: {e}")
            return 0.0
    
    async def _calculate_constitutional_compliance(self, recommendations: List[RecommendationItem]) -> Dict[str, Any]:
        """Calculate constitutional compliance metrics."""
        try:
            if not recommendations:
                return {"compliance_rate": 0.0, "avg_score": 0.0}
            
            # Calculate compliance rate (items above threshold)
            compliant_items = sum(
                1 for r in recommendations 
                if r.constitutional_score >= self.constitutional_threshold
            )
            compliance_rate = compliant_items / len(recommendations)
            
            # Calculate average constitutional score
            avg_score = sum(r.constitutional_score for r in recommendations) / len(recommendations)
            
            return {
                "compliance_rate": compliance_rate,
                "avg_score": avg_score,
                "total_items": len(recommendations),
                "compliant_items": compliant_items,
                "constitutional_threshold": self.constitutional_threshold
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate constitutional compliance: {e}")
            return {"error": str(e)}
    
    async def add_user_interaction(self, interaction: UserInteraction) -> bool:
        """Add user interaction for learning."""
        try:
            # Add to collaborative filtering service
            return await self.collaborative_service.add_interaction(interaction)
            
        except Exception as e:
            logger.error(f"Failed to add user interaction: {e}")
            return False
    
    async def get_recommendation_analytics(self, user_id: str) -> PersonalizationMetrics:
        """Get personalization analytics for a user."""
        try:
            # Mock implementation - would integrate with actual analytics
            return PersonalizationMetrics(
                user_id=user_id,
                diversity_score=0.75,
                novelty_score=0.65,
                coverage_score=0.80,
                constitutional_alignment=0.85,
                satisfaction_score=0.70,
                constitutional_hash=self.constitutional_hash
            )
            
        except Exception as e:
            logger.error(f"Failed to get recommendation analytics: {e}")
            return PersonalizationMetrics(
                user_id=user_id,
                diversity_score=0.0,
                novelty_score=0.0,
                coverage_score=0.0,
                constitutional_alignment=0.0,
                satisfaction_score=0.0,
                constitutional_hash=self.constitutional_hash
            )