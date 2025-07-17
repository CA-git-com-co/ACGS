"""
Collaborative Filtering Service - User-based and item-based recommendations
Constitutional Hash: cdd01ef066bc6cf2
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime, timedelta
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import NMF
import redis
import json
import asyncio

from ..models.schemas import (
    UserInteraction,
    UserProfile,
    ContentItem,
    RecommendationItem,
    RecommendationType,
    ContentType,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class CollaborativeFilteringService:
    """
    Collaborative filtering recommendation service with constitutional compliance.
    Supports both user-based and item-based collaborative filtering.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/2"):
        """Initialize collaborative filtering service."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Storage keys
        self.interaction_key_prefix = "interaction:"
        self.user_profile_key_prefix = "user_profile:"
        self.item_similarity_key_prefix = "item_similarity:"
        self.user_similarity_key_prefix = "user_similarity:"
        self.rating_matrix_key = "rating_matrix"
        
        # Parameters
        self.min_interactions = 5  # Minimum interactions for recommendations
        self.similarity_threshold = 0.1
        self.constitutional_weight = 0.3
        
        logger.info("CollaborativeFilteringService initialized")
    
    async def add_interaction(self, interaction: UserInteraction) -> bool:
        """Add user interaction to the system."""
        try:
            # Store interaction
            interaction_key = f"{self.interaction_key_prefix}{interaction.user_id}:{interaction.content_id}"
            interaction_data = {
                "id": interaction.id,
                "user_id": interaction.user_id,
                "content_id": interaction.content_id,
                "interaction_type": interaction.interaction_type.value,
                "rating": interaction.rating,
                "timestamp": interaction.timestamp.isoformat(),
                "constitutional_compliant": interaction.constitutional_compliant,
                "constitutional_hash": self.constitutional_hash
            }
            
            self.redis_client.set(interaction_key, json.dumps(interaction_data))
            
            # Update user profile
            await self._update_user_profile(interaction.user_id, interaction)
            
            logger.info(f"Added interaction: {interaction.user_id} -> {interaction.content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add interaction: {e}")
            return False
    
    async def get_user_based_recommendations(self, user_id: str, limit: int = 10) -> List[RecommendationItem]:
        """Generate recommendations based on similar users."""
        try:
            # Get user interactions
            user_interactions = await self._get_user_interactions(user_id)
            
            if len(user_interactions) < self.min_interactions:
                return await self._get_popular_recommendations(limit)
            
            # Find similar users
            similar_users = await self._find_similar_users(user_id, limit=20)
            
            # Get recommendations from similar users
            recommendations = {}
            
            for similar_user_id, similarity_score in similar_users:
                similar_user_interactions = await self._get_user_interactions(similar_user_id)
                
                for interaction in similar_user_interactions:
                    content_id = interaction["content_id"]
                    
                    # Skip if user already interacted with this content
                    if any(i["content_id"] == content_id for i in user_interactions):
                        continue
                    
                    # Calculate weighted score
                    rating = interaction.get("rating", 3.0)
                    constitutional_score = 1.0 if interaction.get("constitutional_compliant", True) else 0.5
                    
                    weighted_score = (
                        similarity_score * rating * constitutional_score
                    ) / 5.0  # Normalize to 0-1
                    
                    if content_id not in recommendations:
                        recommendations[content_id] = {
                            "score": weighted_score,
                            "count": 1,
                            "constitutional_score": constitutional_score
                        }
                    else:
                        recommendations[content_id]["score"] += weighted_score
                        recommendations[content_id]["count"] += 1
            
            # Average scores and sort
            for content_id in recommendations:
                recommendations[content_id]["score"] /= recommendations[content_id]["count"]
            
            # Sort by score and limit
            sorted_recommendations = sorted(
                recommendations.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )[:limit]
            
            # Build recommendation items
            result = []
            for content_id, data in sorted_recommendations:
                item = RecommendationItem(
                    content_id=content_id,
                    title=f"Content {content_id}",  # TODO: Get actual title
                    description=f"Recommended based on similar users",
                    content_type=ContentType.DOCUMENT,  # TODO: Get actual type
                    score=data["score"],
                    confidence=min(1.0, data["count"] / 10.0),  # Confidence based on count
                    reason=f"Users similar to you also liked this content",
                    constitutional_score=data["constitutional_score"]
                )
                result.append(item)
            
            return result
            
        except Exception as e:
            logger.error(f"User-based recommendations failed: {e}")
            return []
    
    async def get_item_based_recommendations(self, user_id: str, limit: int = 10) -> List[RecommendationItem]:
        """Generate recommendations based on item similarities."""
        try:
            # Get user interactions
            user_interactions = await self._get_user_interactions(user_id)
            
            if len(user_interactions) < self.min_interactions:
                return await self._get_popular_recommendations(limit)
            
            # Get items user has interacted with
            user_items = [i["content_id"] for i in user_interactions]
            
            # Find similar items for each user item
            recommendations = {}
            
            for content_id in user_items:
                similar_items = await self._find_similar_items(content_id, limit=20)
                
                for similar_item_id, similarity_score in similar_items:
                    # Skip if user already interacted with this item
                    if similar_item_id in user_items:
                        continue
                    
                    # Get constitutional score for item
                    constitutional_score = await self._get_item_constitutional_score(similar_item_id)
                    
                    # Calculate weighted score
                    user_rating = next(
                        (i.get("rating", 3.0) for i in user_interactions if i["content_id"] == content_id),
                        3.0
                    )
                    
                    weighted_score = (
                        similarity_score * (user_rating / 5.0) * constitutional_score
                    )
                    
                    if similar_item_id not in recommendations:
                        recommendations[similar_item_id] = {
                            "score": weighted_score,
                            "count": 1,
                            "constitutional_score": constitutional_score
                        }
                    else:
                        recommendations[similar_item_id]["score"] += weighted_score
                        recommendations[similar_item_id]["count"] += 1
            
            # Average scores and sort
            for content_id in recommendations:
                recommendations[content_id]["score"] /= recommendations[content_id]["count"]
            
            # Sort by score and limit
            sorted_recommendations = sorted(
                recommendations.items(),
                key=lambda x: x[1]["score"],
                reverse=True
            )[:limit]
            
            # Build recommendation items
            result = []
            for content_id, data in sorted_recommendations:
                item = RecommendationItem(
                    content_id=content_id,
                    title=f"Content {content_id}",  # TODO: Get actual title
                    description=f"Recommended based on similar items",
                    content_type=ContentType.DOCUMENT,  # TODO: Get actual type
                    score=data["score"],
                    confidence=min(1.0, data["count"] / 5.0),
                    reason=f"Based on items similar to ones you've liked",
                    constitutional_score=data["constitutional_score"]
                )
                result.append(item)
            
            return result
            
        except Exception as e:
            logger.error(f"Item-based recommendations failed: {e}")
            return []
    
    async def train_matrix_factorization(self, n_components: int = 50) -> bool:
        """Train matrix factorization model for recommendations."""
        try:
            # Build rating matrix
            rating_matrix = await self._build_rating_matrix()
            
            if rating_matrix.empty:
                logger.warning("No data available for matrix factorization")
                return False
            
            # Apply NMF
            nmf = NMF(n_components=n_components, random_state=42)
            user_features = nmf.fit_transform(rating_matrix.values)
            item_features = nmf.components_
            
            # Store features
            await self._store_matrix_features(user_features, item_features, rating_matrix)
            
            logger.info("Matrix factorization training completed")
            return True
            
        except Exception as e:
            logger.error(f"Matrix factorization training failed: {e}")
            return False
    
    async def _get_user_interactions(self, user_id: str) -> List[Dict]:
        """Get all interactions for a user."""
        try:
            interactions = []
            
            # Search for user interactions
            pattern = f"{self.interaction_key_prefix}{user_id}:*"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                interaction_data = self.redis_client.get(key)
                if interaction_data:
                    interaction = json.loads(interaction_data)
                    interactions.append(interaction)
            
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to get user interactions: {e}")
            return []
    
    async def _find_similar_users(self, user_id: str, limit: int = 10) -> List[Tuple[str, float]]:
        """Find users similar to the given user."""
        try:
            # Get user interactions
            user_interactions = await self._get_user_interactions(user_id)
            user_items = {i["content_id"]: i.get("rating", 3.0) for i in user_interactions}
            
            # Find all other users
            pattern = f"{self.user_profile_key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            similarities = []
            
            for key in keys:
                other_user_id = key.replace(self.user_profile_key_prefix, "")
                if other_user_id == user_id:
                    continue
                
                # Get other user interactions
                other_interactions = await self._get_user_interactions(other_user_id)
                other_items = {i["content_id"]: i.get("rating", 3.0) for i in other_interactions}
                
                # Calculate similarity
                similarity = self._calculate_user_similarity(user_items, other_items)
                
                if similarity > self.similarity_threshold:
                    similarities.append((other_user_id, similarity))
            
            # Sort by similarity and limit
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar users: {e}")
            return []
    
    async def _find_similar_items(self, content_id: str, limit: int = 10) -> List[Tuple[str, float]]:
        """Find items similar to the given item."""
        try:
            # Get users who interacted with this item
            item_users = await self._get_item_users(content_id)
            
            # Find items that these users also interacted with
            similar_items = {}
            
            for user_id in item_users:
                user_interactions = await self._get_user_interactions(user_id)
                
                for interaction in user_interactions:
                    other_content_id = interaction["content_id"]
                    if other_content_id != content_id:
                        if other_content_id not in similar_items:
                            similar_items[other_content_id] = 0
                        similar_items[other_content_id] += 1
            
            # Calculate similarities based on co-occurrence
            similarities = []
            total_users = len(item_users)
            
            for other_content_id, count in similar_items.items():
                similarity = count / total_users  # Jaccard-like similarity
                if similarity > self.similarity_threshold:
                    similarities.append((other_content_id, similarity))
            
            # Sort by similarity and limit
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to find similar items: {e}")
            return []
    
    async def _get_item_users(self, content_id: str) -> List[str]:
        """Get all users who interacted with an item."""
        try:
            users = []
            
            # Search for interactions with this content
            pattern = f"{self.interaction_key_prefix}*:{content_id}"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                # Extract user_id from key
                user_id = key.replace(self.interaction_key_prefix, "").split(":")[0]
                users.append(user_id)
            
            return users
            
        except Exception as e:
            logger.error(f"Failed to get item users: {e}")
            return []
    
    def _calculate_user_similarity(self, user1_items: Dict, user2_items: Dict) -> float:
        """Calculate similarity between two users based on their interactions."""
        try:
            # Find common items
            common_items = set(user1_items.keys()) & set(user2_items.keys())
            
            if len(common_items) == 0:
                return 0.0
            
            # Calculate cosine similarity
            user1_ratings = [user1_items[item] for item in common_items]
            user2_ratings = [user2_items[item] for item in common_items]
            
            # Convert to numpy arrays
            vec1 = np.array(user1_ratings)
            vec2 = np.array(user2_ratings)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"User similarity calculation failed: {e}")
            return 0.0
    
    async def _get_item_constitutional_score(self, content_id: str) -> float:
        """Get constitutional score for an item."""
        try:
            # TODO: Integrate with actual constitutional scoring service
            # For now, return a mock score
            return 0.8
            
        except Exception as e:
            logger.error(f"Failed to get constitutional score: {e}")
            return 0.5
    
    async def _get_popular_recommendations(self, limit: int = 10) -> List[RecommendationItem]:
        """Get popular recommendations for cold start."""
        try:
            # Get all interactions and count by content
            pattern = f"{self.interaction_key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            content_counts = {}
            
            for key in keys:
                interaction_data = self.redis_client.get(key)
                if interaction_data:
                    interaction = json.loads(interaction_data)
                    content_id = interaction["content_id"]
                    
                    if content_id not in content_counts:
                        content_counts[content_id] = 0
                    content_counts[content_id] += 1
            
            # Sort by popularity
            sorted_content = sorted(
                content_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            # Build recommendation items
            result = []
            for content_id, count in sorted_content:
                item = RecommendationItem(
                    content_id=content_id,
                    title=f"Popular Content {content_id}",
                    description="Popular content based on user interactions",
                    content_type=ContentType.DOCUMENT,
                    score=min(1.0, count / 100.0),  # Normalize popularity
                    confidence=0.5,  # Medium confidence for popular items
                    reason="Popular among users",
                    constitutional_score=0.8  # Default constitutional score
                )
                result.append(item)
            
            return result
            
        except Exception as e:
            logger.error(f"Popular recommendations failed: {e}")
            return []
    
    async def _update_user_profile(self, user_id: str, interaction: UserInteraction):
        """Update user profile with new interaction."""
        try:
            profile_key = f"{self.user_profile_key_prefix}{user_id}"
            profile_data = self.redis_client.get(profile_key)
            
            if profile_data:
                profile = json.loads(profile_data)
            else:
                profile = {
                    "user_id": user_id,
                    "interaction_count": 0,
                    "content_types": {},
                    "avg_rating": 0.0,
                    "constitutional_compliant_rate": 1.0,
                    "last_updated": datetime.utcnow().isoformat(),
                    "constitutional_hash": self.constitutional_hash
                }
            
            # Update profile
            profile["interaction_count"] += 1
            profile["last_updated"] = datetime.utcnow().isoformat()
            
            # Update constitutional compliance rate
            compliant_count = profile.get("compliant_count", 0)
            if interaction.constitutional_compliant:
                compliant_count += 1
            
            profile["compliant_count"] = compliant_count
            profile["constitutional_compliant_rate"] = compliant_count / profile["interaction_count"]
            
            # Store updated profile
            self.redis_client.set(profile_key, json.dumps(profile))
            
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
    
    async def _build_rating_matrix(self) -> pd.DataFrame:
        """Build user-item rating matrix."""
        try:
            # Get all interactions
            pattern = f"{self.interaction_key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            interactions = []
            
            for key in keys:
                interaction_data = self.redis_client.get(key)
                if interaction_data:
                    interaction = json.loads(interaction_data)
                    interactions.append({
                        "user_id": interaction["user_id"],
                        "content_id": interaction["content_id"],
                        "rating": interaction.get("rating", 3.0)
                    })
            
            if not interactions:
                return pd.DataFrame()
            
            # Create DataFrame and pivot to rating matrix
            df = pd.DataFrame(interactions)
            rating_matrix = df.pivot_table(
                index="user_id",
                columns="content_id",
                values="rating",
                fill_value=0
            )
            
            return rating_matrix
            
        except Exception as e:
            logger.error(f"Failed to build rating matrix: {e}")
            return pd.DataFrame()
    
    async def _store_matrix_features(self, user_features: np.ndarray, item_features: np.ndarray, rating_matrix: pd.DataFrame):
        """Store matrix factorization features."""
        try:
            # Store user features
            for i, user_id in enumerate(rating_matrix.index):
                feature_key = f"user_features:{user_id}"
                features = user_features[i].tolist()
                self.redis_client.set(feature_key, json.dumps(features))
            
            # Store item features
            for i, content_id in enumerate(rating_matrix.columns):
                feature_key = f"item_features:{content_id}"
                features = item_features[:, i].tolist()
                self.redis_client.set(feature_key, json.dumps(features))
            
            logger.info("Matrix features stored successfully")
            
        except Exception as e:
            logger.error(f"Failed to store matrix features: {e}")
    
    async def get_collaborative_stats(self) -> Dict[str, Any]:
        """Get collaborative filtering statistics."""
        try:
            # Count interactions
            pattern = f"{self.interaction_key_prefix}*"
            total_interactions = len(self.redis_client.keys(pattern))
            
            # Count users
            pattern = f"{self.user_profile_key_prefix}*"
            total_users = len(self.redis_client.keys(pattern))
            
            # Count items
            items = set()
            pattern = f"{self.interaction_key_prefix}*"
            keys = self.redis_client.keys(pattern)
            
            for key in keys:
                interaction_data = self.redis_client.get(key)
                if interaction_data:
                    interaction = json.loads(interaction_data)
                    items.add(interaction["content_id"])
            
            return {
                "total_interactions": total_interactions,
                "total_users": total_users,
                "total_items": len(items),
                "constitutional_hash": self.constitutional_hash
            }
            
        except Exception as e:
            logger.error(f"Failed to get collaborative stats: {e}")
            return {"error": str(e)}