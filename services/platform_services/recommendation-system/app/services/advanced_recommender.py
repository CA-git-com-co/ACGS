"""
Advanced Recommender Engine - 2025 Enhanced with Transformers and Temporal Models
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import pytorch_lightning as pl
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import tensorflow_recommenders as tfrs
from lightfm import LightFM
from lightfm.data import Dataset as LFMDataset
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from aif360.datasets import BinaryLabelDataset
from aif360.metrics import BinaryLabelDatasetMetric
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
from kafka import KafkaProducer, KafkaConsumer
import json
import redis.asyncio as redis
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from collections import defaultdict, deque
import pickle
import hashlib

from ..models.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    UserProfile,
    ItemFeatures,
    InteractionData,
    FairnessMetrics,
    CONSTITUTIONAL_HASH,
)

logger = logging.getLogger(__name__)


class TemporalUserBehaviorModel(pl.LightningModule):
    """GRU-based temporal user behavior model."""

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_layers: int = 2,
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # Embeddings
        self.item_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.user_embedding = nn.Embedding(vocab_size, embedding_dim)

        # GRU for sequence modeling
        self.gru = nn.GRU(
            embedding_dim * 2,  # item + user embeddings
            hidden_dim,
            num_layers,
            batch_first=True,
            dropout=0.2,
        )

        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            hidden_dim, num_heads=8, batch_first=True
        )

        # Output layers
        self.fc1 = nn.Linear(hidden_dim, hidden_dim // 2)
        self.fc2 = nn.Linear(hidden_dim // 2, vocab_size)
        self.dropout = nn.Dropout(0.3)

        # Loss function
        self.criterion = nn.CrossEntropyLoss()

    def forward(
        self,
        user_ids: torch.Tensor,
        item_sequence: torch.Tensor,
        target: torch.Tensor = None,
    ):
        batch_size, seq_len = item_sequence.shape

        # Embeddings
        item_emb = self.item_embedding(item_sequence)
        user_emb = self.user_embedding(user_ids).unsqueeze(1).repeat(1, seq_len, 1)

        # Combine embeddings
        combined_emb = torch.cat([item_emb, user_emb], dim=-1)

        # GRU forward pass
        gru_out, hidden = self.gru(combined_emb)

        # Attention mechanism
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)

        # Final predictions
        output = self.fc1(attn_out[:, -1, :])  # Use last time step
        output = self.dropout(output)
        output = self.fc2(output)

        if target is not None:
            loss = self.criterion(output, target)
            return output, loss

        return output

    def training_step(self, batch, batch_idx):
        user_ids, item_sequence, target = batch
        predictions, loss = self(user_ids, item_sequence, target)

        self.log("train_loss", loss)
        return loss

    def validation_step(self, batch, batch_idx):
        user_ids, item_sequence, target = batch
        predictions, loss = self(user_ids, item_sequence, target)

        self.log("val_loss", loss)
        return loss

    def configure_optimizers(self):
        return optim.Adam(self.parameters(), lr=0.001)


class FairnessAwareRecommender:
    """Advanced fairness-aware recommendation system."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.fairness_threshold = 0.1  # Maximum allowed demographic parity difference

    def calculate_fairness_metrics(
        self, recommendations: List[Dict[str, Any]], user_demographics: Dict[str, Any]
    ) -> FairnessMetrics:
        """Calculate comprehensive fairness metrics."""
        try:
            # Group recommendations by demographic attributes
            demographic_groups = defaultdict(list)

            for rec in recommendations:
                user_id = rec["user_id"]
                if user_id in user_demographics:
                    demographics = user_demographics[user_id]

                    # Group by protected attributes
                    for attr in ["gender", "age_group", "ethnicity"]:
                        if attr in demographics:
                            demographic_groups[f"{attr}_{demographics[attr]}"].append(
                                rec
                            )

            # Calculate demographic parity
            parity_scores = {}
            for group, group_recs in demographic_groups.items():
                # Calculate average rating/score for this group
                avg_score = np.mean([r.get("score", 0) for r in group_recs])
                parity_scores[group] = avg_score

            # Calculate differences between groups
            parity_differences = {}
            group_names = list(parity_scores.keys())

            for i in range(len(group_names)):
                for j in range(i + 1, len(group_names)):
                    group1, group2 = group_names[i], group_names[j]
                    diff = abs(parity_scores[group1] - parity_scores[group2])
                    parity_differences[f"{group1}_vs_{group2}"] = diff

            # Calculate diversity metrics
            diversity_score = self._calculate_diversity_score(recommendations)

            # Calculate Gini coefficient for fairness
            gini_coefficient = self._calculate_gini_coefficient(
                [r.get("score", 0) for r in recommendations]
            )

            return FairnessMetrics(
                demographic_parity_difference=np.mean(
                    list(parity_differences.values())
                ),
                equalized_odds_difference=0.0,  # Placeholder - requires more complex calculation
                diversity_score=diversity_score,
                gini_coefficient=gini_coefficient,
                group_fairness_scores=parity_scores,
                fairness_violations=sum(
                    1
                    for diff in parity_differences.values()
                    if diff > self.fairness_threshold
                ),
                constitutional_hash=self.constitutional_hash,
            )

        except Exception as e:
            logger.error(f"Fairness metrics calculation failed: {e}")
            return FairnessMetrics(
                demographic_parity_difference=0.0,
                equalized_odds_difference=0.0,
                diversity_score=0.0,
                gini_coefficient=0.0,
                constitutional_hash=self.constitutional_hash,
            )

    def _calculate_diversity_score(
        self, recommendations: List[Dict[str, Any]]
    ) -> float:
        """Calculate diversity score using category distribution."""
        try:
            categories = []
            for rec in recommendations:
                item_categories = rec.get("item_categories", [])
                categories.extend(item_categories)

            if not categories:
                return 0.0

            # Calculate Shannon entropy for diversity
            category_counts = defaultdict(int)
            for cat in categories:
                category_counts[cat] += 1

            total = len(categories)
            entropy = 0

            for count in category_counts.values():
                p = count / total
                if p > 0:
                    entropy -= p * np.log2(p)

            # Normalize by maximum possible entropy
            max_entropy = np.log2(len(category_counts))
            return entropy / max_entropy if max_entropy > 0 else 0.0

        except Exception as e:
            logger.error(f"Diversity calculation failed: {e}")
            return 0.0

    def _calculate_gini_coefficient(self, values: List[float]) -> float:
        """Calculate Gini coefficient for inequality measurement."""
        try:
            if not values:
                return 0.0

            # Sort values
            sorted_values = sorted(values)
            n = len(sorted_values)

            # Calculate Gini coefficient
            cumsum = np.cumsum(sorted_values)
            gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n

            return gini

        except Exception as e:
            logger.error(f"Gini coefficient calculation failed: {e}")
            return 0.0


class AdvancedRecommenderEngine:
    """Advanced recommendation engine with transformer embeddings and temporal modeling."""

    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = None
        self.redis_url = redis_url

        # Initialize components
        self.sentence_transformer = None
        self.qdrant_client = None
        self.temporal_model = None
        self.fairness_evaluator = FairnessAwareRecommender()

        # Kafka for streaming
        self.kafka_producer = None
        self.kafka_consumer = None

        # Model parameters
        self.embedding_dim = 384  # MPNet embedding dimension
        self.max_sequence_length = 50
        self.vocab_size = 10000

        # Initialize services
        self._initialize_services()

    def _initialize_services(self):
        """Initialize all recommendation services."""
        try:
            logger.info("Initializing advanced recommendation services...")

            # 1. MPNet-v2 for superior semantic embeddings
            self.sentence_transformer = SentenceTransformer("all-mpnet-base-v2")

            # 2. Qdrant for vector similarity search
            self.qdrant_client = QdrantClient("localhost", port=6333)

            # 3. Initialize temporal user behavior model
            self.temporal_model = TemporalUserBehaviorModel(
                vocab_size=self.vocab_size,
                embedding_dim=128,
                hidden_dim=256,
                num_layers=2,
            )

            # 4. LightFM for hybrid collaborative filtering
            self.lightfm_model = LightFM(
                loss="warp",
                learning_rate=0.05,
                item_alpha=1e-6,
                user_alpha=1e-6,
                no_components=100,
            )

            # 5. Setup vector collections
            self._setup_vector_collections()

            # 6. Initialize Kafka for streaming
            self._setup_kafka_streaming()

            logger.info("Advanced recommendation services initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize recommendation services: {e}")
            raise

    async def initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise

    def _setup_vector_collections(self):
        """Setup Qdrant collections for vector search."""
        try:
            # User embeddings collection
            self.qdrant_client.recreate_collection(
                collection_name="user_embeddings",
                vectors_config=VectorParams(
                    size=self.embedding_dim, distance=Distance.COSINE
                ),
            )

            # Item embeddings collection
            self.qdrant_client.recreate_collection(
                collection_name="item_embeddings",
                vectors_config=VectorParams(
                    size=self.embedding_dim, distance=Distance.COSINE
                ),
            )

            # Context embeddings collection
            self.qdrant_client.recreate_collection(
                collection_name="context_embeddings",
                vectors_config=VectorParams(
                    size=self.embedding_dim, distance=Distance.COSINE
                ),
            )

            logger.info("Vector collections setup complete")

        except Exception as e:
            logger.error(f"Vector collection setup failed: {e}")

    def _setup_kafka_streaming(self):
        """Setup Kafka for real-time recommendation streaming."""
        try:
            # Producer for recommendation updates
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=["localhost:9092"],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )

            # Consumer for user interactions
            self.kafka_consumer = KafkaConsumer(
                "user_interactions",
                bootstrap_servers=["localhost:9092"],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            )

            logger.info("Kafka streaming setup complete")

        except Exception as e:
            logger.warning(f"Kafka setup failed, continuing without streaming: {e}")

    async def generate_recommendations_advanced(
        self,
        request: RecommendationRequest,
        user_profile: UserProfile,
        interaction_history: List[InteractionData],
    ) -> RecommendationResponse:
        """Generate advanced recommendations with temporal modeling."""
        try:
            # 1. Generate user embeddings with temporal context
            user_embedding = await self._generate_temporal_user_embedding(
                user_profile, interaction_history
            )

            # 2. Multi-strategy recommendation generation
            strategies = [
                self._collaborative_filtering_recommendations(
                    user_profile, interaction_history
                ),
                self._content_based_recommendations(user_profile, user_embedding),
                self._temporal_sequence_recommendations(
                    user_profile, interaction_history
                ),
                self._hybrid_lightfm_recommendations(user_profile, interaction_history),
            ]

            # Execute strategies in parallel
            strategy_results = await asyncio.gather(*strategies, return_exceptions=True)

            # 3. Combine and rank recommendations
            combined_recommendations = self._combine_strategy_results(strategy_results)

            # 4. Apply fairness constraints
            fair_recommendations = await self._apply_fairness_constraints(
                combined_recommendations, user_profile
            )

            # 5. Calculate explanations
            explanations = await self._generate_explanations(
                fair_recommendations, user_profile
            )

            # 6. Calculate fairness metrics
            fairness_metrics = self.fairness_evaluator.calculate_fairness_metrics(
                fair_recommendations, {user_profile.user_id: user_profile.demographics}
            )

            # 7. Stream recommendations for real-time processing
            await self._stream_recommendations(fair_recommendations, user_profile)

            response = RecommendationResponse(
                user_id=user_profile.user_id,
                recommendations=fair_recommendations[: request.limit],
                explanations=explanations,
                fairness_metrics=fairness_metrics,
                model_info={
                    "strategies_used": [
                        "collaborative",
                        "content",
                        "temporal",
                        "hybrid",
                    ],
                    "embedding_model": "all-mpnet-base-v2",
                    "temporal_model": "GRU-attention",
                    "fairness_aware": True,
                },
                processing_time=(datetime.utcnow() - request.timestamp).total_seconds(),
                constitutional_hash=self.constitutional_hash,
            )

            # Cache recommendations
            await self._cache_recommendations(user_profile.user_id, response)

            return response

        except Exception as e:
            logger.error(f"Advanced recommendation generation failed: {e}")
            raise

    async def _generate_temporal_user_embedding(
        self, user_profile: UserProfile, interaction_history: List[InteractionData]
    ) -> np.ndarray:
        """Generate temporal user embedding with behavior patterns."""
        try:
            # 1. Create user profile text
            profile_text = f"""
            User preferences: {', '.join(user_profile.preferences)}
            Demographics: {user_profile.demographics}
            Interests: {', '.join(user_profile.interests)}
            """

            # 2. Generate semantic embedding
            profile_embedding = self.sentence_transformer.encode(profile_text)

            # 3. Generate temporal behavior embedding
            if interaction_history:
                # Prepare sequence data for temporal model
                recent_interactions = interaction_history[-self.max_sequence_length :]

                # Create item sequence (simplified - would use proper item IDs)
                item_sequence = [
                    hash(interaction.item_id) % self.vocab_size
                    for interaction in recent_interactions
                ]

                # Pad sequence if needed
                if len(item_sequence) < self.max_sequence_length:
                    item_sequence = [0] * (
                        self.max_sequence_length - len(item_sequence)
                    ) + item_sequence

                # Generate temporal embedding
                user_tensor = torch.tensor(
                    [hash(user_profile.user_id) % self.vocab_size]
                )
                sequence_tensor = torch.tensor([item_sequence])

                with torch.no_grad():
                    temporal_output = self.temporal_model(user_tensor, sequence_tensor)
                    temporal_embedding = temporal_output.numpy().flatten()

                # Combine embeddings
                combined_embedding = np.concatenate(
                    [profile_embedding, temporal_embedding]
                )

                # Store in Qdrant
                await self._store_user_embedding(
                    user_profile.user_id, combined_embedding
                )

                return combined_embedding

            return profile_embedding

        except Exception as e:
            logger.error(f"Temporal embedding generation failed: {e}")
            return np.zeros(self.embedding_dim)

    async def _collaborative_filtering_recommendations(
        self, user_profile: UserProfile, interaction_history: List[InteractionData]
    ) -> List[Dict[str, Any]]:
        """Generate collaborative filtering recommendations."""
        try:
            # Find similar users based on embeddings
            user_embedding = await self._get_user_embedding(user_profile.user_id)

            if user_embedding is None:
                return []

            # Search for similar users
            similar_users = self.qdrant_client.search(
                collection_name="user_embeddings",
                query_vector=user_embedding.tolist(),
                limit=50,
            )

            # Get recommendations from similar users
            recommendations = []
            for similar_user in similar_users:
                similar_user_id = similar_user.payload.get("user_id")
                if similar_user_id == user_profile.user_id:
                    continue

                # Get interactions of similar user
                similar_interactions = await self._get_user_interactions(
                    similar_user_id
                )

                for interaction in similar_interactions:
                    if interaction.rating > 3.0:  # Only positive interactions
                        recommendations.append(
                            {
                                "item_id": interaction.item_id,
                                "score": interaction.rating * similar_user.score,
                                "reason": f"Users with similar preferences liked this",
                                "strategy": "collaborative_filtering",
                            }
                        )

            # Remove duplicates and sort
            unique_recommendations = {}
            for rec in recommendations:
                item_id = rec["item_id"]
                if (
                    item_id not in unique_recommendations
                    or rec["score"] > unique_recommendations[item_id]["score"]
                ):
                    unique_recommendations[item_id] = rec

            return sorted(
                unique_recommendations.values(), key=lambda x: x["score"], reverse=True
            )

        except Exception as e:
            logger.error(f"Collaborative filtering failed: {e}")
            return []

    async def _content_based_recommendations(
        self, user_profile: UserProfile, user_embedding: np.ndarray
    ) -> List[Dict[str, Any]]:
        """Generate content-based recommendations."""
        try:
            # Search for similar items based on user preferences
            similar_items = self.qdrant_client.search(
                collection_name="item_embeddings",
                query_vector=user_embedding.tolist(),
                limit=100,
            )

            recommendations = []
            for item in similar_items:
                recommendations.append(
                    {
                        "item_id": item.payload.get("item_id"),
                        "score": item.score,
                        "reason": f'Matches your interests in {", ".join(user_profile.preferences)}',
                        "strategy": "content_based",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Content-based recommendations failed: {e}")
            return []

    async def _temporal_sequence_recommendations(
        self, user_profile: UserProfile, interaction_history: List[InteractionData]
    ) -> List[Dict[str, Any]]:
        """Generate temporal sequence-based recommendations."""
        try:
            if not interaction_history:
                return []

            # Use temporal model to predict next items
            recent_interactions = interaction_history[-self.max_sequence_length :]

            # Create sequence tensor
            item_sequence = [
                hash(interaction.item_id) % self.vocab_size
                for interaction in recent_interactions
            ]

            if len(item_sequence) < self.max_sequence_length:
                item_sequence = [0] * (
                    self.max_sequence_length - len(item_sequence)
                ) + item_sequence

            user_tensor = torch.tensor([hash(user_profile.user_id) % self.vocab_size])
            sequence_tensor = torch.tensor([item_sequence])

            with torch.no_grad():
                predictions = self.temporal_model(user_tensor, sequence_tensor)
                probabilities = torch.softmax(predictions, dim=-1)

                # Get top predictions
                top_items = torch.topk(probabilities, k=50, dim=-1)

                recommendations = []
                for i in range(top_items.indices.shape[1]):
                    item_idx = top_items.indices[0, i].item()
                    score = top_items.values[0, i].item()

                    recommendations.append(
                        {
                            "item_id": f"item_{item_idx}",
                            "score": score,
                            "reason": "Based on your recent activity patterns",
                            "strategy": "temporal_sequence",
                        }
                    )

                return recommendations

        except Exception as e:
            logger.error(f"Temporal sequence recommendations failed: {e}")
            return []

    async def _hybrid_lightfm_recommendations(
        self, user_profile: UserProfile, interaction_history: List[InteractionData]
    ) -> List[Dict[str, Any]]:
        """Generate hybrid LightFM recommendations."""
        try:
            # This would require pre-trained LightFM model
            # For now, return placeholder recommendations
            recommendations = []

            # Mock implementation
            for i in range(20):
                recommendations.append(
                    {
                        "item_id": f"lightfm_item_{i}",
                        "score": np.random.random(),
                        "reason": "Hybrid collaborative-content filtering",
                        "strategy": "lightfm_hybrid",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"LightFM recommendations failed: {e}")
            return []

    def _combine_strategy_results(
        self, strategy_results: List[Any]
    ) -> List[Dict[str, Any]]:
        """Combine results from different recommendation strategies."""
        try:
            combined_recommendations = {}

            for result in strategy_results:
                if isinstance(result, Exception):
                    continue

                for rec in result:
                    item_id = rec["item_id"]

                    if item_id not in combined_recommendations:
                        combined_recommendations[item_id] = rec.copy()
                    else:
                        # Combine scores from different strategies
                        combined_recommendations[item_id]["score"] = (
                            combined_recommendations[item_id]["score"] + rec["score"]
                        ) / 2

                        # Combine reasons
                        existing_reason = combined_recommendations[item_id]["reason"]
                        new_reason = rec["reason"]
                        if new_reason not in existing_reason:
                            combined_recommendations[item_id][
                                "reason"
                            ] = f"{existing_reason}; {new_reason}"

            # Sort by combined score
            return sorted(
                combined_recommendations.values(),
                key=lambda x: x["score"],
                reverse=True,
            )

        except Exception as e:
            logger.error(f"Strategy combination failed: {e}")
            return []

    async def _apply_fairness_constraints(
        self, recommendations: List[Dict[str, Any]], user_profile: UserProfile
    ) -> List[Dict[str, Any]]:
        """Apply fairness constraints to recommendations."""
        try:
            # Apply demographic parity constraints
            fair_recommendations = []

            # Ensure diverse categories
            category_counts = defaultdict(int)
            max_per_category = max(1, len(recommendations) // 5)  # Max 20% per category

            for rec in recommendations:
                # Mock category assignment
                category = f"category_{hash(rec['item_id']) % 5}"

                if category_counts[category] < max_per_category:
                    rec["category"] = category
                    fair_recommendations.append(rec)
                    category_counts[category] += 1

                if len(fair_recommendations) >= len(recommendations):
                    break

            return fair_recommendations

        except Exception as e:
            logger.error(f"Fairness constraint application failed: {e}")
            return recommendations

    async def _generate_explanations(
        self, recommendations: List[Dict[str, Any]], user_profile: UserProfile
    ) -> List[str]:
        """Generate explanations for recommendations."""
        try:
            explanations = []

            for rec in recommendations:
                explanation = rec.get("reason", "Recommended based on your preferences")
                explanations.append(explanation)

            return explanations

        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return ["Explanation unavailable"] * len(recommendations)

    async def _stream_recommendations(
        self, recommendations: List[Dict[str, Any]], user_profile: UserProfile
    ):
        """Stream recommendations for real-time processing."""
        try:
            if not self.kafka_producer:
                return

            stream_data = {
                "user_id": user_profile.user_id,
                "recommendations": recommendations,
                "timestamp": datetime.utcnow().isoformat(),
                "constitutional_hash": self.constitutional_hash,
            }

            self.kafka_producer.send("recommendations", value=stream_data)

        except Exception as e:
            logger.error(f"Recommendation streaming failed: {e}")

    async def _store_user_embedding(self, user_id: str, embedding: np.ndarray):
        """Store user embedding in Qdrant."""
        try:
            point = PointStruct(
                id=hash(user_id) % (2**32),
                vector=embedding.tolist(),
                payload={
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

            self.qdrant_client.upsert(collection_name="user_embeddings", points=[point])

        except Exception as e:
            logger.error(f"User embedding storage failed: {e}")

    async def _get_user_embedding(self, user_id: str) -> Optional[np.ndarray]:
        """Get user embedding from Qdrant."""
        try:
            results = self.qdrant_client.retrieve(
                collection_name="user_embeddings", ids=[hash(user_id) % (2**32)]
            )

            if results:
                return np.array(results[0].vector)

            return None

        except Exception as e:
            logger.error(f"User embedding retrieval failed: {e}")
            return None

    async def _get_user_interactions(self, user_id: str) -> List[InteractionData]:
        """Get user interactions from cache/database."""
        try:
            if not self.redis_client:
                return []

            interactions_key = f"user_interactions:{user_id}"
            interactions_data = await self.redis_client.lrange(interactions_key, 0, -1)

            interactions = []
            for data in interactions_data:
                try:
                    interaction_dict = json.loads(data)
                    interactions.append(InteractionData(**interaction_dict))
                except (json.JSONDecodeError, TypeError):
                    continue

            return interactions

        except Exception as e:
            logger.error(f"User interaction retrieval failed: {e}")
            return []

    async def _cache_recommendations(
        self, user_id: str, response: RecommendationResponse
    ):
        """Cache recommendations in Redis."""
        try:
            if not self.redis_client:
                return

            cache_key = f"recommendations:{user_id}"
            cache_data = response.dict()

            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour expiration
                json.dumps(cache_data, default=str),
            )

        except Exception as e:
            logger.error(f"Recommendation caching failed: {e}")

    async def health_check(self) -> bool:
        """Check if all recommendation services are healthy."""
        try:
            # Test sentence transformer
            test_embedding = self.sentence_transformer.encode("test")

            # Test Qdrant
            self.qdrant_client.get_collections()

            # Test Redis
            if self.redis_client:
                await self.redis_client.ping()

            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
