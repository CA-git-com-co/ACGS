"""
Vector Service - Manages vector embeddings and similarity search
Constitutional Hash: cdd01ef066bc6cf2
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer
import redis
import json
import asyncio
from datetime import datetime

from ..models.schemas import (
    ContentItem,
    SimilaritySearchRequest,
    SimilaritySearchResult,
    VectorIndexRequest,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class VectorService:
    """
    Vector embedding service for content similarity and constitutional compliance.
    Supports both local Redis storage and external vector databases.
    """
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379/1",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize vector service with embedding model and storage."""
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Vector storage keys
        self.vector_key_prefix = "vector:"
        self.metadata_key_prefix = "metadata:"
        self.index_key = "vector_index"
        
        logger.info(f"VectorService initialized with dimension {self.embedding_dim}")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text content."""
        try:
            # Run embedding generation in thread pool to avoid blocking
            embedding = await asyncio.get_event_loop().run_in_executor(
                None, self.embedding_model.encode, text
            )
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return [0.0] * self.embedding_dim
    
    async def index_content(self, content: ContentItem) -> bool:
        """Index content with its embedding vector."""
        try:
            # Generate embedding if not provided
            if not content.embedding:
                text_content = f"{content.title} {content.description or ''}"
                content.embedding = await self.generate_embedding(text_content)
            
            # Store vector
            vector_key = f"{self.vector_key_prefix}{content.id}"
            self.redis_client.set(vector_key, json.dumps(content.embedding))
            
            # Store metadata
            metadata = {
                "id": content.id,
                "title": content.title,
                "description": content.description,
                "content_type": content.content_type.value,
                "tags": content.tags,
                "metadata": content.metadata,
                "constitutional_score": content.constitutional_score,
                "created_at": content.created_at.isoformat(),
                "constitutional_hash": self.constitutional_hash
            }
            
            metadata_key = f"{self.metadata_key_prefix}{content.id}"
            self.redis_client.set(metadata_key, json.dumps(metadata))
            
            # Add to index
            self.redis_client.sadd(self.index_key, content.id)
            
            logger.info(f"Indexed content: {content.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index content {content.id}: {e}")
            return False
    
    async def search_similar(self, request: SimilaritySearchRequest) -> List[SimilaritySearchResult]:
        """Search for similar content using vector similarity."""
        try:
            results = []
            
            # Get all indexed content IDs
            content_ids = self.redis_client.smembers(self.index_key)
            
            # Calculate similarities
            similarities = []
            for content_id in content_ids:
                vector_key = f"{self.vector_key_prefix}{content_id}"
                vector_data = self.redis_client.get(vector_key)
                
                if vector_data:
                    content_vector = json.loads(vector_data)
                    similarity = self._calculate_cosine_similarity(
                        request.query_vector, content_vector
                    )
                    
                    if similarity >= request.threshold:
                        similarities.append((content_id, similarity))
            
            # Sort by similarity and limit results
            similarities.sort(key=lambda x: x[1], reverse=True)
            similarities = similarities[:request.limit]
            
            # Build results
            for content_id, similarity in similarities:
                metadata_key = f"{self.metadata_key_prefix}{content_id}"
                metadata_data = self.redis_client.get(metadata_key)
                
                if metadata_data:
                    metadata = json.loads(metadata_data)
                    
                    # Apply filters
                    if request.content_type and metadata["content_type"] != request.content_type.value:
                        continue
                    
                    # Create content item
                    content_item = ContentItem(
                        id=metadata["id"],
                        title=metadata["title"],
                        description=metadata.get("description"),
                        content_type=metadata["content_type"],
                        tags=metadata.get("tags", []),
                        metadata=metadata.get("metadata", {}),
                        constitutional_score=metadata.get("constitutional_score", 0.0),
                        created_at=datetime.fromisoformat(metadata["created_at"])
                    )
                    
                    # Calculate combined score
                    constitutional_score = metadata.get("constitutional_score", 0.0)
                    combined_score = (
                        similarity * (1 - request.constitutional_weight) +
                        constitutional_score * request.constitutional_weight
                    )
                    
                    result = SimilaritySearchResult(
                        content_id=content_id,
                        similarity_score=similarity,
                        constitutional_score=constitutional_score,
                        combined_score=combined_score,
                        content=content_item
                    )
                    
                    results.append(result)
            
            # Sort by combined score
            results.sort(key=lambda x: x.combined_score, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []
    
    async def search_similar_to_content(self, content_id: str, limit: int = 10) -> List[SimilaritySearchResult]:
        """Find content similar to a given content item."""
        try:
            # Get content vector
            vector_key = f"{self.vector_key_prefix}{content_id}"
            vector_data = self.redis_client.get(vector_key)
            
            if not vector_data:
                return []
            
            query_vector = json.loads(vector_data)
            
            # Create search request
            search_request = SimilaritySearchRequest(
                query_vector=query_vector,
                limit=limit + 1,  # +1 to exclude the original content
                threshold=0.1,
                constitutional_hash=self.constitutional_hash
            )
            
            # Perform search
            results = await self.search_similar(search_request)
            
            # Exclude the original content
            results = [r for r in results if r.content_id != content_id]
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Similar content search failed: {e}")
            return []
    
    async def get_content_by_ids(self, content_ids: List[str]) -> List[ContentItem]:
        """Get content items by their IDs."""
        try:
            content_items = []
            
            for content_id in content_ids:
                metadata_key = f"{self.metadata_key_prefix}{content_id}"
                metadata_data = self.redis_client.get(metadata_key)
                
                if metadata_data:
                    metadata = json.loads(metadata_data)
                    
                    content_item = ContentItem(
                        id=metadata["id"],
                        title=metadata["title"],
                        description=metadata.get("description"),
                        content_type=metadata["content_type"],
                        tags=metadata.get("tags", []),
                        metadata=metadata.get("metadata", {}),
                        constitutional_score=metadata.get("constitutional_score", 0.0),
                        created_at=datetime.fromisoformat(metadata["created_at"])
                    )
                    
                    content_items.append(content_item)
            
            return content_items
            
        except Exception as e:
            logger.error(f"Failed to get content by IDs: {e}")
            return []
    
    async def update_constitutional_scores(self, content_scores: Dict[str, float]) -> int:
        """Update constitutional scores for content items."""
        try:
            updated_count = 0
            
            for content_id, score in content_scores.items():
                metadata_key = f"{self.metadata_key_prefix}{content_id}"
                metadata_data = self.redis_client.get(metadata_key)
                
                if metadata_data:
                    metadata = json.loads(metadata_data)
                    metadata["constitutional_score"] = score
                    
                    self.redis_client.set(metadata_key, json.dumps(metadata))
                    updated_count += 1
            
            logger.info(f"Updated constitutional scores for {updated_count} items")
            return updated_count
            
        except Exception as e:
            logger.error(f"Failed to update constitutional scores: {e}")
            return 0
    
    async def remove_content(self, content_id: str) -> bool:
        """Remove content from vector index."""
        try:
            # Remove from index
            self.redis_client.srem(self.index_key, content_id)
            
            # Remove vector and metadata
            vector_key = f"{self.vector_key_prefix}{content_id}"
            metadata_key = f"{self.metadata_key_prefix}{content_id}"
            
            self.redis_client.delete(vector_key)
            self.redis_client.delete(metadata_key)
            
            logger.info(f"Removed content: {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove content {content_id}: {e}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector index."""
        try:
            total_items = self.redis_client.scard(self.index_key)
            
            # Get content type distribution
            content_types = {}
            content_ids = self.redis_client.smembers(self.index_key)
            
            for content_id in content_ids:
                metadata_key = f"{self.metadata_key_prefix}{content_id}"
                metadata_data = self.redis_client.get(metadata_key)
                
                if metadata_data:
                    metadata = json.loads(metadata_data)
                    content_type = metadata.get("content_type", "unknown")
                    content_types[content_type] = content_types.get(content_type, 0) + 1
            
            return {
                "total_items": total_items,
                "embedding_dimension": self.embedding_dim,
                "content_types": content_types,
                "constitutional_hash": self.constitutional_hash
            }
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {"error": str(e)}
    
    def _calculate_cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            vec1 = np.array(vector1)
            vec2 = np.array(vector2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            
            # Ensure similarity is between 0 and 1
            return max(0.0, min(1.0, similarity))
            
        except Exception as e:
            logger.error(f"Cosine similarity calculation failed: {e}")
            return 0.0
    
    async def batch_index_content(self, content_items: List[ContentItem]) -> int:
        """Index multiple content items in batch."""
        try:
            indexed_count = 0
            
            for content in content_items:
                if await self.index_content(content):
                    indexed_count += 1
            
            logger.info(f"Batch indexed {indexed_count} content items")
            return indexed_count
            
        except Exception as e:
            logger.error(f"Batch indexing failed: {e}")
            return 0
    
    async def cleanup_expired_content(self, expiry_days: int = 30) -> int:
        """Clean up expired content from index."""
        try:
            cleaned_count = 0
            cutoff_date = datetime.utcnow().timestamp() - (expiry_days * 24 * 60 * 60)
            
            content_ids = self.redis_client.smembers(self.index_key)
            
            for content_id in content_ids:
                metadata_key = f"{self.metadata_key_prefix}{content_id}"
                metadata_data = self.redis_client.get(metadata_key)
                
                if metadata_data:
                    metadata = json.loads(metadata_data)
                    created_at = datetime.fromisoformat(metadata["created_at"])
                    
                    if created_at.timestamp() < cutoff_date:
                        if await self.remove_content(content_id):
                            cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} expired content items")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Content cleanup failed: {e}")
            return 0