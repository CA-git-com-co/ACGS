"""
Policy Generation Cache

Specialized caching for policy generation results with constitutional compliance tracking.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .cache_manager import CacheManager, get_cache_manager

logger = logging.getLogger(__name__)


class PolicyGenerationCache:
    """
    Specialized cache for policy generation results.
    
    Provides intelligent caching for policy generation with constitutional
    compliance validation and semantic similarity detection.
    """
    
    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """Initialize policy generation cache."""
        self.cache_manager = cache_manager or get_cache_manager()
        self.cache_prefix = "policy"
        
        # Cache TTL settings (in seconds)
        self.ttl_settings = {
            "policy_generation": 3600,      # 1 hour
            "constitutional_validation": 1800,  # 30 minutes
            "representation_cache": 7200,   # 2 hours
            "semantic_similarity": 3600,    # 1 hour
            "consensus_results": 1800,      # 30 minutes
        }
        
        logger.info("Policy generation cache initialized")
    
    async def cache_policy_generation(
        self,
        generation_id: str,
        policy_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache complete policy generation result.
        
        Args:
            generation_id: Unique generation identifier
            policy_data: Complete policy generation data
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = f"generation:{generation_id}"
        ttl = ttl or self.ttl_settings["policy_generation"]
        
        # Add caching metadata
        cache_data = {
            **policy_data,
            "cached_at": datetime.utcnow().isoformat(),
            "cache_ttl": ttl,
            "constitutional_hash": self.cache_manager.constitutional_hash
        }
        
        success = await self.cache_manager.set(
            cache_key,
            cache_data,
            ttl=ttl,
            prefix=self.cache_prefix
        )
        
        if success:
            logger.info(f"✅ Cached policy generation: {generation_id}")
            
            # Also cache by semantic hash for similarity detection
            if "semantic_hash" in policy_data:
                semantic_key = f"semantic:{policy_data['semantic_hash']}"
                await self.cache_manager.set(
                    semantic_key,
                    {"generation_id": generation_id, "cached_at": datetime.utcnow().isoformat()},
                    ttl=self.ttl_settings["semantic_similarity"],
                    prefix=self.cache_prefix
                )
        
        return success
    
    async def get_policy_generation(self, generation_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached policy generation result.
        
        Args:
            generation_id: Unique generation identifier
            
        Returns:
            Cached policy data or None if not found
        """
        cache_key = f"generation:{generation_id}"
        
        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)
        
        if cached_data:
            # Validate constitutional hash
            cached_hash = cached_data.get("constitutional_hash")
            if cached_hash != self.cache_manager.constitutional_hash:
                logger.warning(f"Constitutional hash mismatch for cached policy {generation_id}")
                await self.invalidate_policy_generation(generation_id)
                return None
            
            logger.info(f"✅ Retrieved cached policy generation: {generation_id}")
            return cached_data
        
        return None
    
    async def cache_constitutional_validation(
        self,
        policy_content: str,
        validation_result: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache constitutional validation result.
        
        Args:
            policy_content: Policy content for key generation
            validation_result: Validation result data
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if cached successfully, False otherwise
        """
        # Generate cache key from policy content hash
        content_hash = self.cache_manager._hash_key(policy_content)
        cache_key = f"validation:{content_hash}"
        ttl = ttl or self.ttl_settings["constitutional_validation"]
        
        cache_data = {
            **validation_result,
            "cached_at": datetime.utcnow().isoformat(),
            "constitutional_hash": self.cache_manager.constitutional_hash
        }
        
        success = await self.cache_manager.set(
            cache_key,
            cache_data,
            ttl=ttl,
            prefix=self.cache_prefix
        )
        
        if success:
            logger.info(f"✅ Cached constitutional validation: {content_hash}")
        
        return success
    
    async def get_constitutional_validation(self, policy_content: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached constitutional validation result.
        
        Args:
            policy_content: Policy content for key generation
            
        Returns:
            Cached validation data or None if not found
        """
        content_hash = self.cache_manager._hash_key(policy_content)
        cache_key = f"validation:{content_hash}"
        
        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)
        
        if cached_data:
            # Validate constitutional hash
            cached_hash = cached_data.get("constitutional_hash")
            if cached_hash != self.cache_manager.constitutional_hash:
                logger.warning(f"Constitutional hash mismatch for cached validation {content_hash}")
                await self.cache_manager.delete(cache_key, prefix=self.cache_prefix)
                return None
            
            logger.info(f"✅ Retrieved cached constitutional validation: {content_hash}")
            return cached_data
        
        return None
    
    async def cache_representation_set(
        self,
        request_hash: str,
        representation_data: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache representation set for reuse.
        
        Args:
            request_hash: Hash of the generation request
            representation_data: Representation set data
            ttl: Time to live in seconds (optional)
            
        Returns:
            True if cached successfully, False otherwise
        """
        cache_key = f"representations:{request_hash}"
        ttl = ttl or self.ttl_settings["representation_cache"]
        
        cache_data = {
            **representation_data,
            "cached_at": datetime.utcnow().isoformat(),
            "constitutional_hash": self.cache_manager.constitutional_hash
        }
        
        success = await self.cache_manager.set(
            cache_key,
            cache_data,
            ttl=ttl,
            prefix=self.cache_prefix
        )
        
        if success:
            logger.info(f"✅ Cached representation set: {request_hash}")
        
        return success
    
    async def get_representation_set(self, request_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached representation set.
        
        Args:
            request_hash: Hash of the generation request
            
        Returns:
            Cached representation data or None if not found
        """
        cache_key = f"representations:{request_hash}"
        
        cached_data = await self.cache_manager.get(cache_key, prefix=self.cache_prefix)
        
        if cached_data:
            # Validate constitutional hash
            cached_hash = cached_data.get("constitutional_hash")
            if cached_hash != self.cache_manager.constitutional_hash:
                logger.warning(f"Constitutional hash mismatch for cached representations {request_hash}")
                await self.cache_manager.delete(cache_key, prefix=self.cache_prefix)
                return None
            
            logger.info(f"✅ Retrieved cached representation set: {request_hash}")
            return cached_data
        
        return None
    
    async def find_similar_policies(self, semantic_hash: str) -> List[str]:
        """
        Find policies with similar semantic hashes.
        
        Args:
            semantic_hash: Semantic hash to search for
            
        Returns:
            List of generation IDs with similar semantic content
        """
        # Search for exact semantic hash match
        semantic_key = f"semantic:{semantic_hash}"
        exact_match = await self.cache_manager.get(semantic_key, prefix=self.cache_prefix)
        
        if exact_match:
            return [exact_match["generation_id"]]
        
        # TODO: Implement fuzzy semantic similarity search
        # This would require more advanced caching with semantic embeddings
        
        return []
    
    async def invalidate_policy_generation(self, generation_id: str) -> bool:
        """
        Invalidate cached policy generation and related data.
        
        Args:
            generation_id: Generation ID to invalidate
            
        Returns:
            True if invalidated successfully, False otherwise
        """
        cache_key = f"generation:{generation_id}"
        
        # Get the policy data to find related cache entries
        policy_data = await self.get_policy_generation(generation_id)
        
        success = await self.cache_manager.delete(cache_key, prefix=self.cache_prefix)
        
        if success and policy_data:
            # Also invalidate semantic hash cache
            if "semantic_hash" in policy_data:
                semantic_key = f"semantic:{policy_data['semantic_hash']}"
                await self.cache_manager.delete(semantic_key, prefix=self.cache_prefix)
            
            logger.info(f"✅ Invalidated policy generation cache: {generation_id}")
        
        return success
    
    async def invalidate_constitutional_changes(self) -> int:
        """
        Invalidate all cached data when constitutional changes occur.
        
        Returns:
            Number of cache entries invalidated
        """
        # Invalidate all policy-related caches
        patterns = [
            "generation:*",
            "validation:*", 
            "representations:*",
            "semantic:*",
            "consensus:*"
        ]
        
        total_invalidated = 0
        for pattern in patterns:
            invalidated = await self.cache_manager.invalidate_pattern(
                pattern, 
                prefix=self.cache_prefix
            )
            total_invalidated += invalidated
        
        logger.info(f"✅ Invalidated {total_invalidated} cache entries due to constitutional changes")
        return total_invalidated
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get policy cache statistics and performance metrics."""
        base_metrics = await self.cache_manager.get_metrics()
        
        # Add policy-specific metrics
        policy_metrics = {
            "policy_cache_statistics": {
                "ttl_settings": self.ttl_settings,
                "constitutional_hash": self.cache_manager.constitutional_hash,
                "cache_prefix": self.cache_prefix,
            }
        }
        
        return {**base_metrics, **policy_metrics}
