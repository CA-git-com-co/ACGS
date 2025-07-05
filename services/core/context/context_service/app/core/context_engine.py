"""
Context Engine - Core Orchestration

High-performance context management engine that orchestrates storage,
retrieval, search, and lifecycle management for the ACGS context system.
"""

import asyncio
import hashlib
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from .storage_manager import MultiTierStorageManager
from .embedding_service import EmbeddingService
from .vector_store import QdrantVectorStore
from ..models.context_models import (
    BaseContext,
    ContextType,
    ContextPriority,
    ContextStatus,
    ContextSearchQuery,
    ContextSearchResult,
    ContextStats,
    ConversationContext,
    DomainContext,
    ConstitutionalContext,
    AgentContext,
    PolicyContext,
)
from ..models.storage_models import StorageTier

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ContextEngine:
    """
    High-performance context management engine for ACGS.
    
    Features:
    - Sub-50ms context retrieval with multi-tier storage
    - Semantic search with vector similarity and hybrid ranking
    - Hierarchical context management with TTL
    - Constitutional compliance validation
    - WINA optimization integration
    - Real-time context streaming
    """
    
    def __init__(
        self,
        storage_config: Optional[Dict[str, Any]] = None,
        enable_streaming: bool = True,
        enable_wina_optimization: bool = True,
        enable_constitutional_validation: bool = True,
        search_cache_ttl_minutes: int = 15,
        max_search_results: int = 100,
    ):
        """
        Initialize context engine.
        
        Args:
            storage_config: Configuration for storage tiers
            enable_streaming: Enable real-time context streaming
            enable_wina_optimization: Enable WINA optimization
            enable_constitutional_validation: Enable constitutional compliance
            search_cache_ttl_minutes: Search result cache TTL
            max_search_results: Maximum search results to return
        """
        self.storage_config = storage_config or {}
        self.enable_streaming = enable_streaming
        self.enable_wina_optimization = enable_wina_optimization
        self.enable_constitutional_validation = enable_constitutional_validation
        self.search_cache_ttl_minutes = search_cache_ttl_minutes
        self.max_search_results = max_search_results
        
        # Core components
        self.storage_manager: Optional[MultiTierStorageManager] = None
        self.embedding_service: Optional[EmbeddingService] = None
        self.event_streaming = None  # Will be initialized with existing ACGS streaming
        self.constitutional_validator = None  # Will be initialized with AC service
        
        # Performance metrics
        self.metrics = {
            "contexts_stored": 0,
            "contexts_retrieved": 0,
            "contexts_updated": 0,
            "contexts_deleted": 0,
            "searches_performed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_store_latency_ms": 0.0,
            "average_retrieve_latency_ms": 0.0,
            "average_search_latency_ms": 0.0,
            "constitutional_violations": 0,
            "wina_optimizations": 0,
            "total_latency_ms": 0.0,
        }
        
        # Search result cache
        self.search_cache: Dict[str, Tuple[List[ContextSearchResult], datetime]] = {}
        
        # Context type factories
        self.context_factories = {
            ContextType.CONVERSATION: ConversationContext,
            ContextType.DOMAIN: DomainContext,
            ContextType.CONSTITUTIONAL: ConstitutionalContext,
            ContextType.AGENT: AgentContext,
            ContextType.POLICY: PolicyContext,
        }
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
    
    async def initialize(self) -> bool:
        """
        Initialize context engine and all components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing ACGS Context Engine")
            
            # Initialize storage manager
            self.storage_manager = MultiTierStorageManager(**self.storage_config)
            storage_success = await self.storage_manager.initialize()
            
            if not storage_success:
                logger.error("Failed to initialize storage manager")
                return False
            
            # Get embedding service from storage manager
            self.embedding_service = self.storage_manager.embedding_service
            
            # Initialize event streaming if enabled
            if self.enable_streaming:
                await self._initialize_event_streaming()
            
            # Initialize constitutional validation if enabled
            if self.enable_constitutional_validation:
                await self._initialize_constitutional_validation()
            
            # Start background tasks
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.metrics_task = asyncio.create_task(self._metrics_loop())
            
            logger.info("Context Engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize context engine: {e}")
            return False
    
    async def _initialize_event_streaming(self):
        """Initialize event streaming integration."""
        try:
            from services.shared.streaming.event_streaming_manager import EventStreamingManager
            
            # Initialize with default configuration
            streaming_config = {
                "cluster_id": "acgs-main",
                "environment": "development",
                "default_routing_strategy": "hybrid",
            }
            
            self.event_streaming = EventStreamingManager(streaming_config)
            
            # Initialize the streaming manager
            success = await self.event_streaming.initialize()
            if not success:
                logger.warning("Failed to initialize event streaming manager")
                self.enable_streaming = False
                return
            
            logger.info("Event streaming integration initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize event streaming: {e}")
            self.enable_streaming = False
    
    async def _initialize_constitutional_validation(self):
        """Initialize constitutional compliance validation."""
        try:
            from services.core.constitutional_ai.ac_service.app.services.constitutional_validation_service import ConstitutionalValidationService
            from services.shared.security.enhanced_audit_logging import AuditLogger
            
            # Initialize audit logger
            audit_logger = AuditLogger()
            
            # Initialize constitutional validation service
            self.constitutional_validator = ConstitutionalValidationService(
                audit_logger=audit_logger
            )
            
            logger.info("Constitutional validation service initialized successfully")
        except ImportError as e:
            logger.warning(f"Constitutional validation service not available: {e}")
            self.enable_constitutional_validation = False
        except Exception as e:
            logger.warning(f"Failed to initialize constitutional validation: {e}")
            self.enable_constitutional_validation = False
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate SHA256 hash for content integrity."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _create_context_instance(
        self, 
        context_type: ContextType, 
        **kwargs
    ) -> BaseContext:
        """Create context instance of appropriate type."""
        factory = self.context_factories.get(context_type, BaseContext)
        
        # Set content hash
        if "content" in kwargs:
            kwargs["content_hash"] = self._generate_content_hash(kwargs["content"])
        
        # Set context type
        kwargs["context_type"] = context_type
        
        return factory(**kwargs)
    
    async def store_context(
        self,
        context_type: ContextType,
        content: str,
        priority: ContextPriority = ContextPriority.MEDIUM,
        metadata: Optional[Dict[str, Any]] = None,
        **context_specific_fields
    ) -> Tuple[UUID, Dict[str, Any]]:
        """
        Store new context with intelligent tiering.
        
        Args:
            context_type: Type of context to create
            content: Context content
            priority: Context priority level
            metadata: Additional metadata
            **context_specific_fields: Type-specific fields
            
        Returns:
            Tuple of (context_id, operation_metadata)
        """
        start_time = time.time()
        
        try:
            # Validate constitutional compliance
            if self.enable_constitutional_validation:
                compliance_valid = await self._validate_constitutional_compliance(
                    content, context_type, metadata
                )
                if not compliance_valid:
                    self.metrics["constitutional_violations"] += 1
                    raise ValueError("Content violates constitutional compliance")
            
            # Create context instance
            context = self._create_context_instance(
                context_type=context_type,
                content=content,
                priority=priority,
                **context_specific_fields
            )
            
            # Set metadata if provided
            if metadata:
                for key, value in metadata.items():
                    if hasattr(context.metadata, key):
                        setattr(context.metadata, key, value)
            
            # Store context using storage manager
            success, storage_metadata = await self.storage_manager.store_context(
                context=context,
                generate_embedding=True,
            )
            
            if not success:
                raise RuntimeError(f"Failed to store context: {storage_metadata.get('error')}")
            
            # Publish storage event if streaming enabled
            if self.enable_streaming:
                await self._publish_context_event("context_stored", context, storage_metadata)
            
            # Update metrics
            store_latency = (time.time() - start_time) * 1000
            self._update_metrics("store", store_latency, True)
            
            operation_metadata = {
                "context_id": context.context_id,
                "context_type": context_type.value,
                "storage": storage_metadata,
                "latency_ms": store_latency,
                "constitutional_compliant": True,
                "wina_optimized": storage_metadata.get("embedding", {}).get("wina_optimized", False),
            }
            
            logger.debug(f"Stored context {context.context_id} in {store_latency:.2f}ms")
            return context.context_id, operation_metadata
            
        except Exception as e:
            store_latency = (time.time() - start_time) * 1000
            self._update_metrics("store", store_latency, False)
            logger.error(f"Failed to store context: {e}")
            raise
    
    async def retrieve_context(
        self,
        context_id: UUID,
        include_metadata: bool = True,
        update_access_time: bool = True,
    ) -> Tuple[Optional[BaseContext], Dict[str, Any]]:
        """
        Retrieve context by ID with multi-tier lookup.
        
        Args:
            context_id: Context ID to retrieve
            include_metadata: Include full metadata in response
            update_access_time: Update last access timestamp
            
        Returns:
            Tuple of (context, retrieval_metadata)
        """
        start_time = time.time()
        
        try:
            # Retrieve from storage manager
            context, storage_metadata = await self.storage_manager.retrieve_context(
                context_id=context_id,
                update_access_time=update_access_time,
            )
            
            if not context:
                retrieve_latency = (time.time() - start_time) * 1000
                self._update_metrics("retrieve", retrieve_latency, False)
                return None, {
                    "error": "Context not found",
                    "context_id": str(context_id),
                    "latency_ms": retrieve_latency,
                }
            
            # Check if context has expired
            if context.is_expired():
                context.status = ContextStatus.EXPIRED
                # Optionally remove expired context
                await self._handle_expired_context(context)
            
            # Publish retrieval event if streaming enabled
            if self.enable_streaming:
                await self._publish_context_event("context_retrieved", context, storage_metadata)
            
            # Update metrics
            retrieve_latency = (time.time() - start_time) * 1000
            self._update_metrics("retrieve", retrieve_latency, True)
            
            retrieval_metadata = {
                "context_id": str(context.context_id),
                "context_type": context.context_type.value,
                "storage": storage_metadata,
                "latency_ms": retrieve_latency,
                "expired": context.is_expired(),
                "last_accessed": context.accessed_at.isoformat(),
            }
            
            if not include_metadata:
                # Strip sensitive metadata for lightweight responses
                context.metadata = None
                context.embedding_vector = None
            
            logger.debug(f"Retrieved context {context_id} in {retrieve_latency:.2f}ms")
            return context, retrieval_metadata
            
        except Exception as e:
            retrieve_latency = (time.time() - start_time) * 1000
            self._update_metrics("retrieve", retrieve_latency, False)
            logger.error(f"Failed to retrieve context {context_id}: {e}")
            return None, {"error": str(e), "latency_ms": retrieve_latency}
    
    async def search_contexts(
        self,
        query: ContextSearchQuery,
        use_cache: bool = True,
    ) -> Tuple[List[ContextSearchResult], Dict[str, Any]]:
        """
        Search contexts using hybrid semantic and keyword search.
        
        Args:
            query: Search query parameters
            use_cache: Whether to use cached search results
            
        Returns:
            Tuple of (search_results, search_metadata)
        """
        start_time = time.time()
        
        try:
            # Check search cache
            cache_key = self._generate_search_cache_key(query)
            if use_cache and cache_key in self.search_cache:
                cached_results, cache_time = self.search_cache[cache_key]
                cache_age = datetime.utcnow() - cache_time
                
                if cache_age < timedelta(minutes=self.search_cache_ttl_minutes):
                    search_latency = (time.time() - start_time) * 1000
                    self.metrics["cache_hits"] += 1
                    
                    return cached_results, {
                        "total_results": len(cached_results),
                        "latency_ms": search_latency,
                        "cache_hit": True,
                        "cache_age_seconds": cache_age.total_seconds(),
                    }
            
            # Perform search
            results = []
            search_metadata = {
                "semantic_search_used": False,
                "keyword_search_used": False,
                "vector_search_results": 0,
                "keyword_search_results": 0,
                "cache_hit": False,
            }
            
            # Generate query embedding for semantic search
            query_embedding = None
            if query.semantic_search and self.embedding_service:
                embedding_vector, embedding_meta = await self.embedding_service.generate_embedding(
                    query.query_text
                )
                if embedding_vector:
                    query_embedding = embedding_vector
                    search_metadata["semantic_search_used"] = True
            
            # Perform semantic search if embedding available
            semantic_results = []
            if query_embedding and self.storage_manager.vector_store:
                for context_type in query.context_types or list(ContextType):
                    try:
                        # Filter conditions based on query
                        filter_conditions = {}
                        if query.priority_filter:
                            filter_conditions["priority"] = query.priority_filter.value
                        if query.created_after:
                            filter_conditions["created_at"] = {
                                "range": {"gte": query.created_after.isoformat()}
                            }
                        if query.tags_filter:
                            filter_conditions["tags"] = query.tags_filter
                        
                        vector_results = await self.storage_manager.vector_store.search_similar(
                            query_vector=query_embedding,
                            context_type=context_type.value,
                            limit=query.limit,
                            score_threshold=query.similarity_threshold,
                            filter_conditions=filter_conditions,
                        )
                        
                        # Convert to ContextSearchResult
                        for doc, score in vector_results:
                            # Retrieve full context for result
                            context, _ = await self.retrieve_context(
                                doc.context_id, 
                                include_metadata=False,
                                update_access_time=False
                            )
                            
                            if context:
                                result = ContextSearchResult(
                                    context=context,
                                    similarity_score=score,
                                    rank=len(semantic_results) + 1,
                                    matched_keywords=[],
                                    relevance_explanation=f"Semantic similarity: {score:.3f}",
                                )
                                semantic_results.append(result)
                        
                        search_metadata["vector_search_results"] += len(vector_results)
                        
                    except Exception as e:
                        logger.warning(f"Vector search failed for {context_type}: {e}")
            
            # Perform keyword search if enabled
            keyword_results = []
            if query.keyword_search:
                # TODO: Implement keyword search logic
                search_metadata["keyword_search_used"] = True
            
            # Combine and rank results
            all_results = semantic_results + keyword_results
            
            # Apply hybrid ranking (combine semantic and keyword scores)
            all_results = self._apply_hybrid_ranking(all_results, query)
            
            # Apply final filters and pagination
            filtered_results = self._apply_search_filters(all_results, query)
            paginated_results = filtered_results[query.offset:query.offset + query.limit]
            
            # Update ranks
            for i, result in enumerate(paginated_results):
                result.rank = query.offset + i + 1
            
            # Cache results
            if use_cache:
                self.search_cache[cache_key] = (paginated_results, datetime.utcnow())
                # Cleanup old cache entries
                self._cleanup_search_cache()
                self.metrics["cache_misses"] += 1
            
            # Publish search event if streaming enabled
            if self.enable_streaming:
                await self._publish_search_event(query, len(paginated_results))
            
            # Update metrics
            search_latency = (time.time() - start_time) * 1000
            self._update_metrics("search", search_latency, True)
            
            search_metadata.update({
                "total_results": len(paginated_results),
                "latency_ms": search_latency,
                "query_embedding_generated": query_embedding is not None,
                "wina_optimization_applied": False,  # TODO: Track WINA usage
            })
            
            logger.debug(
                f"Search completed: {len(paginated_results)} results in {search_latency:.2f}ms"
            )
            
            return paginated_results, search_metadata
            
        except Exception as e:
            search_latency = (time.time() - start_time) * 1000
            self._update_metrics("search", search_latency, False)
            logger.error(f"Search failed: {e}")
            return [], {"error": str(e), "latency_ms": search_latency}
    
    def _generate_search_cache_key(self, query: ContextSearchQuery) -> str:
        """Generate cache key for search query."""
        query_dict = query.dict()
        query_str = str(sorted(query_dict.items()))
        return hashlib.sha256(query_str.encode()).hexdigest()[:16]
    
    def _apply_hybrid_ranking(
        self, 
        results: List[ContextSearchResult], 
        query: ContextSearchQuery
    ) -> List[ContextSearchResult]:
        """Apply hybrid ranking combining semantic and keyword scores."""
        # TODO: Implement sophisticated hybrid ranking algorithm
        # For now, just sort by similarity score
        return sorted(results, key=lambda r: r.similarity_score, reverse=True)
    
    def _apply_search_filters(
        self, 
        results: List[ContextSearchResult], 
        query: ContextSearchQuery
    ) -> List[ContextSearchResult]:
        """Apply additional search filters."""
        filtered = results
        
        # Filter by context types
        if query.context_types:
            filtered = [r for r in filtered if r.context.context_type in query.context_types]
        
        # Filter by date range
        if query.created_after:
            filtered = [r for r in filtered if r.context.created_at >= query.created_after]
        
        if query.created_before:
            filtered = [r for r in filtered if r.context.created_at <= query.created_before]
        
        # Filter by tags
        if query.tags_filter:
            filtered = [
                r for r in filtered 
                if any(tag in r.context.keywords for tag in query.tags_filter)
            ]
        
        return filtered
    
    def _cleanup_search_cache(self):
        """Remove expired entries from search cache."""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, (_, cache_time) in self.search_cache.items()
            if current_time - cache_time > timedelta(minutes=self.search_cache_ttl_minutes)
        ]
        
        for key in expired_keys:
            del self.search_cache[key]
    
    async def _validate_constitutional_compliance(
        self,
        content: str,
        context_type: ContextType,
        metadata: Optional[Dict[str, Any]]
    ) -> bool:
        """Validate content for constitutional compliance."""
        if not self.enable_constitutional_validation or not hasattr(self, 'constitutional_validator'):
            # Fall back to basic validation
            return await self._basic_compliance_validation(content, context_type)
        
        try:
            from services.core.constitutional_ai.ac_service.app.schemas import ConstitutionalComplianceRequest
            
            # Create compliance request
            compliance_request = ConstitutionalComplianceRequest(
                content=content,
                context={
                    "context_type": context_type.value,
                    "metadata": metadata or {},
                    "source": "context_service",
                    "validation_level": "standard"
                },
                require_formal_verification=(context_type == ContextType.CONSTITUTIONAL),
                principles_to_check=[
                    "CONST-001",  # Democratic Participation
                    "CONST-002",  # Transparency Requirement
                    "CONST-003",  # Constitutional Compliance
                ] if context_type == ContextType.CONSTITUTIONAL else [
                    "CONST-002",  # Transparency Requirement
                    "CONST-003",  # Constitutional Compliance
                ]
            )
            
            # Perform constitutional validation
            validation_result = await asyncio.to_thread(
                self.constitutional_validator.validate_constitutional_compliance,
                compliance_request
            )
            
            # Check validation result
            if hasattr(validation_result, 'is_compliant'):
                is_compliant = validation_result.is_compliant
            elif hasattr(validation_result, 'compliance_status'):
                is_compliant = validation_result.compliance_status == "compliant"
            else:
                # If validation result format is unexpected, default to basic validation
                logger.warning("Unexpected constitutional validation result format")
                return await self._basic_compliance_validation(content, context_type)
            
            if not is_compliant:
                logger.warning(
                    f"Constitutional compliance validation failed for {context_type.value} context"
                )
                
                # Log compliance violation for audit
                if hasattr(self, 'constitutional_validator') and hasattr(self.constitutional_validator, 'audit_logger'):
                    await self.constitutional_validator.audit_logger.log_streaming_event({
                        "event_type": "constitutional_violation_detected",
                        "context_type": context_type.value,
                        "content_hash": hashlib.sha256(content.encode()).hexdigest(),
                        "violation_details": getattr(validation_result, 'violations', []),
                        "timestamp": datetime.utcnow().isoformat(),
                    })
            
            return is_compliant
            
        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            # Fall back to basic validation on error
            return await self._basic_compliance_validation(content, context_type)
    
    async def _basic_compliance_validation(
        self,
        content: str,
        context_type: ContextType
    ) -> bool:
        """Basic compliance validation as fallback."""
        try:
            # Check for sensitive data patterns
            sensitive_patterns = [
                "password", "secret", "api_key", "private_key",
                "ssn", "social_security", "credit_card", "bearer ",
                "oauth", "jwt", "token"
            ]
            
            content_lower = content.lower()
            for pattern in sensitive_patterns:
                if pattern in content_lower:
                    logger.warning(f"Potential sensitive data detected: {pattern}")
                    return False
            
            # Constitutional contexts require additional checks
            if context_type == ContextType.CONSTITUTIONAL:
                # Ensure constitutional content has required structure
                constitutional_keywords = [
                    "principle", "rule", "requirement", "shall", "must",
                    "compliance", "constitutional", "governance"
                ]
                
                has_constitutional_elements = any(
                    keyword in content_lower for keyword in constitutional_keywords
                )
                
                if not has_constitutional_elements:
                    logger.warning("Constitutional context lacks required constitutional elements")
                    return False
            
            # Check content length (prevent extremely long content that might be malicious)
            if len(content) > 100000:  # 100KB limit
                logger.warning("Content exceeds maximum allowed length")
                return False
            
            # Check for potential injection patterns
            injection_patterns = [
                "<script", "javascript:", "eval(", "exec(",
                "sql", "drop table", "delete from", "update set"
            ]
            
            for pattern in injection_patterns:
                if pattern in content_lower:
                    logger.warning(f"Potential injection pattern detected: {pattern}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Basic compliance validation failed: {e}")
            return False
    
    async def _handle_expired_context(self, context: BaseContext):
        """Handle expired context cleanup."""
        try:
            # Mark as expired
            context.status = ContextStatus.EXPIRED
            
            # Optionally archive to L3 storage
            if context.context_type in [ContextType.CONSTITUTIONAL, ContextType.POLICY]:
                # Keep important contexts in archive
                logger.debug(f"Archiving expired context {context.context_id}")
            else:
                # Delete less important contexts
                logger.debug(f"Scheduling deletion of expired context {context.context_id}")
            
        except Exception as e:
            logger.error(f"Failed to handle expired context {context.context_id}: {e}")
    
    async def _publish_context_event(
        self,
        event_type: str,
        context: BaseContext,
        metadata: Dict[str, Any]
    ):
        """Publish context event to streaming system."""
        if not self.enable_streaming or not self.event_streaming:
            return
        
        try:
            from services.shared.streaming.event_streaming_manager import (
                StreamingEvent, EventType, EventPriority, EventRoutingStrategy
            )
            
            # Map string event type to EventType enum
            event_type_map = {
                "context_stored": EventType.CONTEXT_STORED,
                "context_retrieved": EventType.CONTEXT_RETRIEVED,
                "context_updated": EventType.CONTEXT_UPDATED,
                "context_expired": EventType.CONTEXT_EXPIRED,
                "context_archived": EventType.CONTEXT_ARCHIVED,
                "context_deleted": EventType.CONTEXT_DELETED,
            }
            
            streaming_event_type = event_type_map.get(event_type)
            if not streaming_event_type:
                logger.warning(f"Unknown context event type: {event_type}")
                return
            
            # Create streaming event
            streaming_event = StreamingEvent(
                event_id=str(uuid4()),
                event_type=streaming_event_type,
                priority=EventPriority.MEDIUM,
                source_service="context_service",
                target_service=None,
                payload={
                    "context_id": str(context.context_id),
                    "context_type": context.context_type.value,
                    "priority": context.priority.value,
                    "content_hash": context.content_hash,
                    "created_at": context.created_at.isoformat(),
                    "accessed_at": context.accessed_at.isoformat(),
                    "expires_at": context.expires_at.isoformat() if context.expires_at else None,
                },
                metadata={
                    "operation_metadata": metadata,
                    "service_version": "1.0.0",
                    "constitutional_compliant": context.metadata.constitutional_compliant,
                },
                routing_strategy=EventRoutingStrategy.HYBRID,
                constitutional_compliant=context.metadata.constitutional_compliant,
                correlation_id=str(context.context_id),
                timestamp=datetime.utcnow(),
            )
            
            # Publish event
            success = await self.event_streaming.publish_event(streaming_event)
            if success:
                logger.debug(f"Published context event: {event_type} for {context.context_id}")
            else:
                logger.warning(f"Failed to publish context event: {event_type}")
            
        except Exception as e:
            logger.warning(f"Failed to publish context event: {e}")
    
    async def _publish_search_event(
        self,
        query: ContextSearchQuery,
        result_count: int
    ):
        """Publish search event to streaming system."""
        if not self.enable_streaming or not self.event_streaming:
            return
        
        try:
            from services.shared.streaming.event_streaming_manager import (
                StreamingEvent, EventType, EventPriority, EventRoutingStrategy
            )
            
            # Create search event
            streaming_event = StreamingEvent(
                event_id=str(uuid4()),
                event_type=EventType.CONTEXT_SEARCHED,
                priority=EventPriority.LOW,  # Analytics events are low priority
                source_service="context_service",
                target_service=None,
                payload={
                    "query_text": query.query_text,
                    "result_count": result_count,
                    "context_types": [ct.value for ct in query.context_types],
                    "semantic_search": query.semantic_search,
                    "keyword_search": query.keyword_search,
                    "similarity_threshold": query.similarity_threshold,
                    "limit": query.limit,
                    "offset": query.offset,
                },
                metadata={
                    "query_hash": hashlib.sha256(query.query_text.encode()).hexdigest()[:16],
                    "filters_applied": {
                        "priority_filter": query.priority_filter.value if query.priority_filter else None,
                        "created_after": query.created_after.isoformat() if query.created_after else None,
                        "created_before": query.created_before.isoformat() if query.created_before else None,
                        "tags_filter": query.tags_filter,
                    },
                    "wina_optimization": query.apply_wina_optimization,
                },
                routing_strategy=EventRoutingStrategy.NATS_ONLY,  # Analytics use NATS
                constitutional_compliant=True,
                correlation_id=None,
                timestamp=datetime.utcnow(),
            )
            
            # Publish event
            success = await self.event_streaming.publish_event(streaming_event)
            if success:
                logger.debug(f"Published search event: {result_count} results")
            else:
                logger.warning("Failed to publish search event")
            
        except Exception as e:
            logger.warning(f"Failed to publish search event: {e}")
    
    def _update_metrics(self, operation: str, latency_ms: float, success: bool):
        """Update performance metrics."""
        if operation == "store":
            self.metrics["contexts_stored"] += 1
            if success:
                current_avg = self.metrics["average_store_latency_ms"]
                count = self.metrics["contexts_stored"]
                self.metrics["average_store_latency_ms"] = (
                    (current_avg * (count - 1) + latency_ms) / count
                )
        elif operation == "retrieve":
            self.metrics["contexts_retrieved"] += 1
            if success:
                current_avg = self.metrics["average_retrieve_latency_ms"]
                count = self.metrics["contexts_retrieved"]
                self.metrics["average_retrieve_latency_ms"] = (
                    (current_avg * (count - 1) + latency_ms) / count
                )
        elif operation == "search":
            self.metrics["searches_performed"] += 1
            if success:
                current_avg = self.metrics["average_search_latency_ms"]
                count = self.metrics["searches_performed"]
                self.metrics["average_search_latency_ms"] = (
                    (current_avg * (count - 1) + latency_ms) / count
                )
        
        if success:
            self.metrics["total_latency_ms"] += latency_ms
    
    async def get_context_stats(self) -> ContextStats:
        """Get comprehensive context statistics."""
        try:
            # Get storage metrics
            storage_metrics = await self.storage_manager.get_storage_metrics()
            
            # TODO: Calculate actual statistics from storage
            # For now, return basic metrics
            
            return ContextStats(
                total_contexts=self.metrics["contexts_stored"],
                contexts_by_type={
                    ContextType.CONVERSATION: 0,
                    ContextType.DOMAIN: 0,
                    ContextType.CONSTITUTIONAL: 0,
                    ContextType.AGENT: 0,
                    ContextType.POLICY: 0,
                },
                contexts_by_status={
                    ContextStatus.ACTIVE: 0,
                    ContextStatus.ARCHIVED: 0,
                    ContextStatus.EXPIRED: 0,
                    ContextStatus.PENDING: 0,
                },
                total_storage_size=sum(
                    metrics.used_capacity_bytes for metrics in storage_metrics.values()
                ),
                average_context_size=1024.0,  # Placeholder
                average_retrieval_latency_ms=self.metrics["average_retrieve_latency_ms"],
                average_storage_latency_ms=self.metrics["average_store_latency_ms"],
                cache_hit_rate=(
                    self.metrics["cache_hits"] / 
                    max(1, self.metrics["cache_hits"] + self.metrics["cache_misses"])
                ) * 100,
                contexts_accessed_today=self.metrics["contexts_retrieved"],
                most_accessed_types=[ContextType.CONVERSATION, ContextType.DOMAIN],
                expired_contexts_pending_cleanup=0,  # TODO: Calculate from storage
                constitutional_compliance_rate=(
                    (self.metrics["contexts_stored"] - self.metrics["constitutional_violations"]) /
                    max(1, self.metrics["contexts_stored"])
                ) * 100,
                wina_optimization_rate=(
                    self.metrics["wina_optimizations"] / 
                    max(1, self.metrics["contexts_stored"])
                ) * 100,
                collection_timestamp=datetime.utcnow(),
            )
            
        except Exception as e:
            logger.error(f"Failed to get context stats: {e}")
            # Return minimal stats on error
            return ContextStats(
                total_contexts=0,
                contexts_by_type={},
                contexts_by_status={},
                total_storage_size=0,
                average_context_size=0.0,
                average_retrieval_latency_ms=0.0,
                average_storage_latency_ms=0.0,
                cache_hit_rate=0.0,
                contexts_accessed_today=0,
                most_accessed_types=[],
                expired_contexts_pending_cleanup=0,
                constitutional_compliance_rate=100.0,
                wina_optimization_rate=0.0,
                collection_timestamp=datetime.utcnow(),
            )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    async def _cleanup_loop(self):
        """Background task for cleanup operations."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                self._cleanup_search_cache()
                # TODO: Add more cleanup operations
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _metrics_loop(self):
        """Background task for metrics collection."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                # TODO: Collect and publish metrics
                logger.debug("Metrics collection placeholder")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def close(self):
        """Close context engine and cleanup resources."""
        try:
            # Cancel background tasks
            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass
            
            if self.metrics_task:
                self.metrics_task.cancel()
                try:
                    await self.metrics_task
                except asyncio.CancelledError:
                    pass
            
            # Close storage manager
            if self.storage_manager:
                await self.storage_manager.close()
            
            # Clear caches
            self.search_cache.clear()
            
            logger.info("Context Engine closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing context engine: {e}")