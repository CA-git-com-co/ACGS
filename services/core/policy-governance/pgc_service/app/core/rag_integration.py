"""
RAG Rule Generator Integration Module

Integrates the RAG-based rule generator with the existing Policy Governance Compiler
service, providing seamless access to constitutional principle retrieval and 
Rego rule synthesis capabilities.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .rag_rule_generator import RAGRuleGenerator, RegoRuleResult
from ..models.constitutional_principles import ConstitutionalPrinciple, get_constitutional_principles_database

# Constitutional compliance hash for ACGS-2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class RAGIntegrationService:
    """
    Integration service for RAG-based rule generation within PGC.
    
    Provides high-level interface for constitutional principle retrieval
    and Rego rule synthesis with performance optimization and caching.
    """
    
    def __init__(self, enable_caching: bool = True):
        self.rag_generator: Optional[RAGRuleGenerator] = None
        self.enable_caching = enable_caching
        self.rule_cache: Dict[str, RegoRuleResult] = {}
        self.cache_ttl_seconds = 3600  # 1 hour cache TTL
        self.cache_timestamps: Dict[str, float] = {}
        self.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_generation_time_ms": 0.0,
            "human_review_required": 0,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        logger.info("RAG Integration Service initialized")
    
    async def initialize(self):
        """Initialize the RAG integration service."""
        try:
            # Load constitutional principles database
            principles_db = await get_constitutional_principles_database()
            
            # Convert to format expected by RAG generator
            principles_data = []
            for principle in principles_db:
                principle_data = {
                    "id": principle.id,
                    "content": principle.content,
                    "category": principle.category,
                    "priority_weight": principle.priority_weight,
                    "source": principle.source,
                    "version": principle.version,
                    "metadata": principle.metadata or {}
                }
                principles_data.append(principle_data)
            
            # Initialize RAG generator
            self.rag_generator = RAGRuleGenerator(constitutional_principles=principles_data)
            await self.rag_generator.initialize()
            
            logger.info(f"RAG Integration Service initialized with {len(principles_data)} principles")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG Integration Service: {e}")
            raise
    
    async def generate_rule_from_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        risk_threshold: float = 0.55,
        use_cache: bool = True
    ) -> RegoRuleResult:
        """
        Generate Rego rule from natural language query.
        
        Args:
            query: Natural language description of governance requirement
            context: Additional context for rule generation
            risk_threshold: Risk threshold for WINA optimization (0.25-0.55)
            use_cache: Whether to use caching for performance
            
        Returns:
            RegoRuleResult with generated rule and metadata
        """
        if not self.rag_generator:
            await self.initialize()
        
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        # Check cache if enabled
        cache_key = self._generate_cache_key(query, context, risk_threshold)
        if use_cache and self.enable_caching:
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                self.metrics["cache_hits"] += 1
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached_result
        
        self.metrics["cache_misses"] += 1
        
        try:
            # Generate rule using RAG
            result = await self.rag_generator.generate_rego_rule(
                query=query,
                context=context,
                risk_threshold=risk_threshold
            )
            
            # Update metrics
            generation_time = (time.time() - start_time) * 1000
            self._update_metrics(generation_time, result.requires_human_review)
            
            # Cache result if enabled
            if use_cache and self.enable_caching:
                self._cache_result(cache_key, result)
            
            logger.info(f"Generated rule {result.rule_id} with confidence {result.confidence_score:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Rule generation failed for query '{query}': {e}")
            raise
    
    async def retrieve_similar_principles(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve constitutional principles similar to query.
        
        Args:
            query: Search query
            top_k: Maximum number of results
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar principles with metadata
        """
        if not self.rag_generator:
            await self.initialize()
        
        try:
            retrieval_results = await self.rag_generator.retrieve_relevant_principles(
                query=query,
                top_k=top_k,
                similarity_threshold=similarity_threshold
            )
            
            # Convert to API-friendly format
            results = []
            for result in retrieval_results:
                principle_data = {
                    "principle_id": result.principle_id,
                    "content": result.principle_content,
                    "similarity_score": result.similarity_score,
                    "metadata": result.metadata,
                    "constitutional_hash": CONSTITUTIONAL_HASH
                }
                results.append(principle_data)
            
            logger.info(f"Retrieved {len(results)} similar principles for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Principle retrieval failed for query '{query}': {e}")
            raise
    
    async def validate_rule_quality(self, rule_content: str) -> Dict[str, Any]:
        """
        Validate the quality of a generated Rego rule.
        
        Args:
            rule_content: Rego rule content to validate
            
        Returns:
            Validation result with quality metrics
        """
        validation_result = {
            "is_valid": True,
            "quality_score": 0.0,
            "issues": [],
            "suggestions": [],
            "constitutional_compliance": False,
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
        
        try:
            # Check basic Rego structure
            if "package" not in rule_content:
                validation_result["issues"].append("Missing package declaration")
                validation_result["is_valid"] = False
            
            if "allow" not in rule_content and "deny" not in rule_content:
                validation_result["issues"].append("Missing allow/deny rules")
                validation_result["is_valid"] = False
            
            # Check constitutional compliance
            if CONSTITUTIONAL_HASH in rule_content:
                validation_result["constitutional_compliance"] = True
                validation_result["quality_score"] += 0.3
            else:
                validation_result["issues"].append("Missing constitutional hash validation")
                validation_result["suggestions"].append(f"Add constitutional hash check: input.constitutional_hash == \"{CONSTITUTIONAL_HASH}\"")
            
            # Check for security best practices
            if "default allow = false" in rule_content:
                validation_result["quality_score"] += 0.2
            else:
                validation_result["suggestions"].append("Consider using 'default allow = false' for security")
            
            # Check for input validation
            if "input." in rule_content:
                validation_result["quality_score"] += 0.2
            else:
                validation_result["suggestions"].append("Add input validation conditions")
            
            # Check for proper formatting
            if rule_content.count("{") == rule_content.count("}"):
                validation_result["quality_score"] += 0.1
            else:
                validation_result["issues"].append("Mismatched braces in rule structure")
                validation_result["is_valid"] = False
            
            # Final quality assessment
            if validation_result["is_valid"] and len(validation_result["issues"]) == 0:
                validation_result["quality_score"] += 0.2
            
            validation_result["quality_score"] = min(validation_result["quality_score"], 1.0)
            
            logger.debug(f"Rule validation completed with quality score: {validation_result['quality_score']:.2f}")
            
        except Exception as e:
            logger.error(f"Rule validation failed: {e}")
            validation_result["is_valid"] = False
            validation_result["issues"].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _generate_cache_key(self, query: str, context: Optional[Dict[str, Any]], risk_threshold: float) -> str:
        """Generate cache key for request."""
        context_str = str(sorted(context.items())) if context else "none"
        return f"{hash(query)}_{hash(context_str)}_{risk_threshold}"
    
    def _get_cached_result(self, cache_key: str) -> Optional[RegoRuleResult]:
        """Get cached result if valid."""
        if cache_key not in self.rule_cache:
            return None
        
        # Check TTL
        if cache_key in self.cache_timestamps:
            age = time.time() - self.cache_timestamps[cache_key]
            if age > self.cache_ttl_seconds:
                # Remove expired cache entry
                del self.rule_cache[cache_key]
                del self.cache_timestamps[cache_key]
                return None
        
        return self.rule_cache[cache_key]
    
    def _cache_result(self, cache_key: str, result: RegoRuleResult):
        """Cache result with timestamp."""
        self.rule_cache[cache_key] = result
        self.cache_timestamps[cache_key] = time.time()
        
        # Cleanup old cache entries if cache is getting large
        if len(self.rule_cache) > 1000:
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = []
        
        for key, timestamp in self.cache_timestamps.items():
            if current_time - timestamp > self.cache_ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.rule_cache:
                del self.rule_cache[key]
            if key in self.cache_timestamps:
                del self.cache_timestamps[key]
        
        logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _update_metrics(self, generation_time_ms: float, requires_human_review: bool):
        """Update performance metrics."""
        # Update average generation time
        current_avg = self.metrics["avg_generation_time_ms"]
        total_requests = self.metrics["total_requests"]
        
        self.metrics["avg_generation_time_ms"] = (
            (current_avg * (total_requests - 1) + generation_time_ms) / total_requests
        )
        
        # Update human review counter
        if requires_human_review:
            self.metrics["human_review_required"] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get integration service metrics."""
        cache_hit_rate = 0.0
        if self.metrics["total_requests"] > 0:
            cache_hit_rate = self.metrics["cache_hits"] / self.metrics["total_requests"]
        
        metrics = self.metrics.copy()
        metrics.update({
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.rule_cache),
            "human_review_rate": (
                self.metrics["human_review_required"] / max(self.metrics["total_requests"], 1)
            ),
            "rag_generator_metrics": self.rag_generator.get_metrics() if self.rag_generator else {}
        })
        
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of RAG integration service."""
        health_status = {
            "status": "healthy",
            "initialized": self.rag_generator is not None,
            "cache_enabled": self.enable_caching,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": time.time()
        }
        
        try:
            if self.rag_generator:
                # Test basic functionality
                test_query = "test health check query"
                start_time = time.time()
                
                # Test principle retrieval
                principles = await self.retrieve_similar_principles(test_query, top_k=1)
                
                health_status["principle_retrieval_working"] = len(principles) >= 0
                health_status["response_time_ms"] = (time.time() - start_time) * 1000
            else:
                health_status["status"] = "not_initialized"
                
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"RAG Integration health check failed: {e}")
        
        return health_status


# Global instance for service integration
_rag_integration_service: Optional[RAGIntegrationService] = None


async def get_rag_integration_service() -> RAGIntegrationService:
    """Get or create global RAG integration service instance."""
    global _rag_integration_service
    
    if _rag_integration_service is None:
        _rag_integration_service = RAGIntegrationService()
        await _rag_integration_service.initialize()
    
    return _rag_integration_service
