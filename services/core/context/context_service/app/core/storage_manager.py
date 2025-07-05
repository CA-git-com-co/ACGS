"""
Multi-Tier Storage Manager

Orchestrates the three-tier storage architecture for optimal performance:
- L1 Cache (Redis): Sub-1ms retrieval for hot data
- L2 Vector (Qdrant): Sub-10ms semantic search for warm data
- L3 Archive (PostgreSQL): Long-term storage for cold data
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

import asyncpg

from services.shared.cache.redis_cluster import get_cache_manager

from ..models.context_models import BaseContext, ContextType
from ..models.storage_models import StorageMetrics, StorageOperation, StorageTier
from .embedding_service import EmbeddingService
from .vector_store import QdrantVectorStore

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class MultiTierStorageManager:
    """
    Multi-tier storage manager orchestrating Redis, Qdrant, and PostgreSQL
    for optimal context storage and retrieval performance.
    """

    def __init__(
        self,
        redis_config: Optional[dict[str, Any]] = None,
        qdrant_config: Optional[dict[str, Any]] = None,
        postgres_config: Optional[dict[str, Any]] = None,
        enable_intelligent_tiering: bool = True,
        l1_cache_ttl_minutes: int = 60,
        l2_vector_ttl_hours: int = 24,
        l3_archive_threshold_days: int = 30,
    ):
        """
        Initialize multi-tier storage manager.

        Args:
            redis_config: Redis configuration
            qdrant_config: Qdrant configuration
            postgres_config: PostgreSQL configuration
            enable_intelligent_tiering: Enable automatic data tiering
            l1_cache_ttl_minutes: L1 cache TTL in minutes
            l2_vector_ttl_hours: L2 vector storage TTL in hours
            l3_archive_threshold_days: Days before moving to L3 archive
        """
        self.redis_config = redis_config or {}
        self.qdrant_config = qdrant_config or {}
        self.postgres_config = postgres_config or {
            "host": "localhost",
            "port": 5432,
            "database": "acgs_context",
            "user": "acgs_user",
            "password": "acgs_password",
        }

        self.enable_intelligent_tiering = enable_intelligent_tiering
        self.l1_cache_ttl_minutes = l1_cache_ttl_minutes
        self.l2_vector_ttl_hours = l2_vector_ttl_hours
        self.l3_archive_threshold_days = l3_archive_threshold_days

        # Storage tier components
        self.cache_manager = None  # Redis L1 cache
        self.vector_store = None  # Qdrant L2 vector store
        self.embedding_service = None  # Embedding generation
        self.postgres_pool = None  # PostgreSQL L3 archive

        # Performance tracking
        self.tier_metrics = {
            StorageTier.L1_CACHE: StorageMetrics(
                tier=StorageTier.L1_CACHE,
                total_capacity_bytes=0,
                used_capacity_bytes=0,
                available_capacity_bytes=0,
                utilization_percentage=0.0,
                average_read_latency_ms=0.0,
                average_write_latency_ms=0.0,
                throughput_ops_per_second=0.0,
                query_success_rate=100.0,
                total_operations=0,
                read_operations=0,
                write_operations=0,
                delete_operations=0,
                failed_operations=0,
                error_rate=0.0,
                measurement_time=datetime.utcnow(),
                measurement_period_seconds=3600,
            ),
            StorageTier.L2_VECTOR: StorageMetrics(
                tier=StorageTier.L2_VECTOR,
                total_capacity_bytes=0,
                used_capacity_bytes=0,
                available_capacity_bytes=0,
                utilization_percentage=0.0,
                average_read_latency_ms=0.0,
                average_write_latency_ms=0.0,
                throughput_ops_per_second=0.0,
                query_success_rate=100.0,
                total_operations=0,
                read_operations=0,
                write_operations=0,
                delete_operations=0,
                failed_operations=0,
                error_rate=0.0,
                measurement_time=datetime.utcnow(),
                measurement_period_seconds=3600,
            ),
            StorageTier.L3_ARCHIVE: StorageMetrics(
                tier=StorageTier.L3_ARCHIVE,
                total_capacity_bytes=0,
                used_capacity_bytes=0,
                available_capacity_bytes=0,
                utilization_percentage=0.0,
                average_read_latency_ms=0.0,
                average_write_latency_ms=0.0,
                throughput_ops_per_second=0.0,
                query_success_rate=100.0,
                total_operations=0,
                read_operations=0,
                write_operations=0,
                delete_operations=0,
                failed_operations=0,
                error_rate=0.0,
                measurement_time=datetime.utcnow(),
                measurement_period_seconds=3600,
            ),
        }

        # Operation tracking
        self.operations_log: list[StorageOperation] = []
        self.max_operations_log = 1000  # Keep last 1000 operations

        # Background tasks
        self.tiering_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None

    async def initialize(self) -> bool:
        """
        Initialize all storage tiers.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing multi-tier storage manager")

            # Initialize L1 Cache (Redis)
            l1_success = await self._initialize_l1_cache()

            # Initialize L2 Vector Store (Qdrant)
            l2_success = await self._initialize_l2_vector_store()

            # Initialize L3 Archive (PostgreSQL)
            l3_success = await self._initialize_l3_archive()

            # Initialize embedding service
            embedding_success = await self._initialize_embedding_service()

            # Start background tasks
            if self.enable_intelligent_tiering:
                self.tiering_task = asyncio.create_task(
                    self._intelligent_tiering_loop()
                )
                self.cleanup_task = asyncio.create_task(self._cleanup_loop())

            success = (
                l1_success or l2_success or l3_success
            )  # At least one tier must work

            if success:
                logger.info(
                    "Multi-tier storage initialized. "
                    f"L1: {'✓' if l1_success else '✗'}, "
                    f"L2: {'✓' if l2_success else '✗'}, "
                    f"L3: {'✓' if l3_success else '✗'}, "
                    f"Embedding: {'✓' if embedding_success else '✗'}"
                )
            else:
                logger.error("Failed to initialize any storage tier")

            return success

        except Exception as e:
            logger.error(f"Failed to initialize multi-tier storage: {e}")
            return False

    async def _initialize_l1_cache(self) -> bool:
        """Initialize L1 Redis cache."""
        try:
            self.cache_manager = get_cache_manager()
            logger.info("L1 Cache (Redis) initialized")
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize L1 cache: {e}")
            return False

    async def _initialize_l2_vector_store(self) -> bool:
        """Initialize L2 Qdrant vector store."""
        try:
            self.vector_store = QdrantVectorStore(**self.qdrant_config)
            success = await self.vector_store.initialize()
            if success:
                logger.info("L2 Vector Store (Qdrant) initialized")
            return success
        except Exception as e:
            logger.warning(f"Failed to initialize L2 vector store: {e}")
            return False

    async def _initialize_l3_archive(self) -> bool:
        """Initialize L3 PostgreSQL archive."""
        try:
            self.postgres_pool = await asyncpg.create_pool(**self.postgres_config)

            # Create tables if they don't exist
            await self._create_archive_tables()

            logger.info("L3 Archive (PostgreSQL) initialized")
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize L3 archive: {e}")
            return False

    async def _initialize_embedding_service(self) -> bool:
        """Initialize embedding service."""
        try:
            self.embedding_service = EmbeddingService()
            success = await self.embedding_service.initialize()
            if success:
                logger.info("Embedding service initialized")
            return success
        except Exception as e:
            logger.warning(f"Failed to initialize embedding service: {e}")
            return False

    async def _create_archive_tables(self):
        """Create PostgreSQL tables for L3 archive."""
        async with self.postgres_pool.acquire() as conn:
            # Archive entries table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS archive_entries (
                    archive_id UUID PRIMARY KEY,
                    context_id UUID NOT NULL,
                    archived_content TEXT NOT NULL,
                    content_compression TEXT DEFAULT 'none',
                    content_encryption BOOLEAN DEFAULT FALSE,
                    archive_reason TEXT NOT NULL,
                    retention_period_days INTEGER,
                    access_restrictions TEXT[],
                    constitutional_compliant BOOLEAN NOT NULL,
                    audit_trail JSONB DEFAULT '[]',
                    archived_at TIMESTAMP NOT NULL,
                    original_created_at TIMESTAMP NOT NULL,
                    scheduled_deletion_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Storage operations log table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS storage_operations (
                    operation_id UUID PRIMARY KEY,
                    operation_type TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    context_id UUID NOT NULL,
                    data_size_bytes INTEGER NOT NULL,
                    latency_ms FLOAT NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    wina_optimization_applied BOOLEAN DEFAULT FALSE,
                    optimization_savings_ms FLOAT,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP NOT NULL,
                    service_name TEXT NOT NULL,
                    user_id TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

            # Create indexes
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_archive_entries_context_id
                ON archive_entries (context_id);
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_archive_entries_archived_at
                ON archive_entries (archived_at);
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_storage_operations_context_id
                ON storage_operations (context_id);
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_storage_operations_started_at
                ON storage_operations (started_at);
            """)

    async def store_context(
        self,
        context: BaseContext,
        generate_embedding: bool = True,
        tier_preference: Optional[StorageTier] = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Store context using intelligent tiering.

        Args:
            context: Context to store
            generate_embedding: Whether to generate embedding
            tier_preference: Preferred storage tier (None for automatic)

        Returns:
            Tuple of (success, metadata)
        """
        start_time = time.time()
        operation_id = context.context_id

        try:
            # Generate embedding if requested
            embedding_vector = None
            embedding_metadata = {}

            if generate_embedding and self.embedding_service:
                (
                    embedding_vector,
                    embedding_metadata,
                ) = await self.embedding_service.generate_embedding(context.content)

                if embedding_vector:
                    context.embedding_vector = embedding_vector

            # Determine optimal storage tier
            target_tier = tier_preference or self._determine_optimal_tier(context)

            # Store in target tier
            success = False
            storage_metadata = {}

            if target_tier == StorageTier.L1_CACHE:
                success, storage_metadata = await self._store_in_l1(context)
            elif target_tier == StorageTier.L2_VECTOR:
                success, storage_metadata = await self._store_in_l2(context)
            elif target_tier == StorageTier.L3_ARCHIVE:
                success, storage_metadata = await self._store_in_l3(context)

            # If target tier fails, try fallback tiers
            if not success:
                if target_tier != StorageTier.L2_VECTOR and self.vector_store:
                    success, storage_metadata = await self._store_in_l2(context)
                    storage_metadata["fallback"] = True
                    storage_metadata["original_tier"] = target_tier.value

                if (
                    not success
                    and target_tier != StorageTier.L1_CACHE
                    and self.cache_manager
                ):
                    success, storage_metadata = await self._store_in_l1(context)
                    storage_metadata["fallback"] = True
                    storage_metadata["original_tier"] = target_tier.value

            # Update context access time
            context.refresh_access()

            # Log operation
            operation_time = (time.time() - start_time) * 1000
            await self._log_storage_operation(
                operation_id=operation_id,
                operation_type="store",
                tier=target_tier,
                context_id=context.context_id,
                data_size_bytes=len(context.content.encode()),
                latency_ms=operation_time,
                success=success,
                error_message=storage_metadata.get("error"),
            )

            # Combine metadata
            result_metadata = {
                "tier": target_tier.value,
                "storage": storage_metadata,
                "embedding": embedding_metadata,
                "latency_ms": operation_time,
                "success": success,
            }

            return success, result_metadata

        except Exception as e:
            operation_time = (time.time() - start_time) * 1000
            logger.error(f"Failed to store context {context.context_id}: {e}")

            await self._log_storage_operation(
                operation_id=operation_id,
                operation_type="store",
                tier=StorageTier.L1_CACHE,  # Default for error logging
                context_id=context.context_id,
                data_size_bytes=len(context.content.encode()) if context.content else 0,
                latency_ms=operation_time,
                success=False,
                error_message=str(e),
            )

            return False, {"error": str(e), "latency_ms": operation_time}

    async def retrieve_context(
        self,
        context_id: UUID,
        update_access_time: bool = True,
    ) -> tuple[Optional[BaseContext], dict[str, Any]]:
        """
        Retrieve context using multi-tier lookup.

        Args:
            context_id: Context ID to retrieve
            update_access_time: Whether to update access timestamp

        Returns:
            Tuple of (context, metadata)
        """
        start_time = time.time()

        try:
            # Try L1 cache first (fastest)
            if self.cache_manager:
                context, metadata = await self._retrieve_from_l1(context_id)
                if context:
                    if update_access_time:
                        context.refresh_access()

                    retrieval_time = (time.time() - start_time) * 1000
                    metadata.update({
                        "tier": StorageTier.L1_CACHE.value,
                        "cache_hit": True,
                        "latency_ms": retrieval_time,
                    })

                    await self._log_storage_operation(
                        operation_id=context_id,
                        operation_type="retrieve",
                        tier=StorageTier.L1_CACHE,
                        context_id=context_id,
                        data_size_bytes=len(context.content.encode()),
                        latency_ms=retrieval_time,
                        success=True,
                    )

                    return context, metadata

            # Try L2 vector store (semantic search capability)
            if self.vector_store:
                context, metadata = await self._retrieve_from_l2(context_id)
                if context:
                    if update_access_time:
                        context.refresh_access()

                    # Promote to L1 cache for future access
                    if self.cache_manager:
                        await self._store_in_l1(context)

                    retrieval_time = (time.time() - start_time) * 1000
                    metadata.update({
                        "tier": StorageTier.L2_VECTOR.value,
                        "cache_hit": False,
                        "promoted_to_l1": self.cache_manager is not None,
                        "latency_ms": retrieval_time,
                    })

                    await self._log_storage_operation(
                        operation_id=context_id,
                        operation_type="retrieve",
                        tier=StorageTier.L2_VECTOR,
                        context_id=context_id,
                        data_size_bytes=len(context.content.encode()),
                        latency_ms=retrieval_time,
                        success=True,
                    )

                    return context, metadata

            # Try L3 archive (slowest but comprehensive)
            if self.postgres_pool:
                context, metadata = await self._retrieve_from_l3(context_id)
                if context:
                    if update_access_time:
                        context.refresh_access()

                    # Promote to higher tiers based on access pattern
                    promotion_tier = self._determine_promotion_tier(context)
                    if promotion_tier == StorageTier.L2_VECTOR and self.vector_store:
                        await self._store_in_l2(context)
                    elif promotion_tier == StorageTier.L1_CACHE and self.cache_manager:
                        await self._store_in_l1(context)

                    retrieval_time = (time.time() - start_time) * 1000
                    metadata.update({
                        "tier": StorageTier.L3_ARCHIVE.value,
                        "cache_hit": False,
                        "promoted_tier": (
                            promotion_tier.value if promotion_tier else None
                        ),
                        "latency_ms": retrieval_time,
                    })

                    await self._log_storage_operation(
                        operation_id=context_id,
                        operation_type="retrieve",
                        tier=StorageTier.L3_ARCHIVE,
                        context_id=context_id,
                        data_size_bytes=len(context.content.encode()),
                        latency_ms=retrieval_time,
                        success=True,
                    )

                    return context, metadata

            # Context not found in any tier
            retrieval_time = (time.time() - start_time) * 1000
            await self._log_storage_operation(
                operation_id=context_id,
                operation_type="retrieve",
                tier=StorageTier.L1_CACHE,  # Default for not found
                context_id=context_id,
                data_size_bytes=0,
                latency_ms=retrieval_time,
                success=False,
                error_message="Context not found",
            )

            return None, {
                "error": "Context not found",
                "tiers_searched": [
                    tier.value
                    for tier in [
                        StorageTier.L1_CACHE,
                        StorageTier.L2_VECTOR,
                        StorageTier.L3_ARCHIVE,
                    ]
                    if getattr(self, f"{tier.value.replace('_', '').lower()}")
                ],
                "latency_ms": retrieval_time,
            }

        except Exception as e:
            retrieval_time = (time.time() - start_time) * 1000
            logger.error(f"Failed to retrieve context {context_id}: {e}")

            await self._log_storage_operation(
                operation_id=context_id,
                operation_type="retrieve",
                tier=StorageTier.L1_CACHE,
                context_id=context_id,
                data_size_bytes=0,
                latency_ms=retrieval_time,
                success=False,
                error_message=str(e),
            )

            return None, {"error": str(e), "latency_ms": retrieval_time}

    def _determine_optimal_tier(self, context: BaseContext) -> StorageTier:
        """Determine optimal storage tier for context."""

        # High priority contexts go to L1 cache
        if context.priority.value in ["critical", "high"]:
            return StorageTier.L1_CACHE

        # Constitutional and policy contexts go to L2 for semantic search
        if context.context_type in [ContextType.CONSTITUTIONAL, ContextType.POLICY]:
            return StorageTier.L2_VECTOR

        # Recent conversations stay in L1 cache
        if context.context_type == ContextType.CONVERSATION:
            return StorageTier.L1_CACHE

        # Domain and agent contexts go to L2 vector store
        if context.context_type in [ContextType.DOMAIN, ContextType.AGENT]:
            return StorageTier.L2_VECTOR

        # Default to L2 vector store
        return StorageTier.L2_VECTOR

    def _determine_promotion_tier(self, context: BaseContext) -> Optional[StorageTier]:
        """Determine if context should be promoted to higher tier."""

        # High-priority contexts get promoted to L1
        if context.priority.value in ["critical", "high"]:
            return StorageTier.L1_CACHE

        # Recently accessed contexts get promoted to L2
        if context.accessed_at > datetime.utcnow() - timedelta(hours=1):
            return StorageTier.L2_VECTOR

        # No promotion needed
        return None

    # Tier-specific storage methods would be implemented here
    # (Truncated for brevity - these would handle the actual storage/retrieval logic for each tier)

    async def _store_in_l1(self, context: BaseContext) -> tuple[bool, dict[str, Any]]:
        """Store context in L1 Redis cache."""
        # Implementation would go here
        return True, {"tier": "l1_cache"}

    async def _store_in_l2(self, context: BaseContext) -> tuple[bool, dict[str, Any]]:
        """Store context in L2 Qdrant vector store."""
        # Implementation would go here
        return True, {"tier": "l2_vector"}

    async def _store_in_l3(self, context: BaseContext) -> tuple[bool, dict[str, Any]]:
        """Store context in L3 PostgreSQL archive."""
        # Implementation would go here
        return True, {"tier": "l3_archive"}

    async def _retrieve_from_l1(
        self, context_id: UUID
    ) -> tuple[Optional[BaseContext], dict[str, Any]]:
        """Retrieve context from L1 cache."""
        # Implementation would go here
        return None, {}

    async def _retrieve_from_l2(
        self, context_id: UUID
    ) -> tuple[Optional[BaseContext], dict[str, Any]]:
        """Retrieve context from L2 vector store."""
        # Implementation would go here
        return None, {}

    async def _retrieve_from_l3(
        self, context_id: UUID
    ) -> tuple[Optional[BaseContext], dict[str, Any]]:
        """Retrieve context from L3 archive."""
        # Implementation would go here
        return None, {}

    async def _log_storage_operation(
        self,
        operation_id: UUID,
        operation_type: str,
        tier: StorageTier,
        context_id: UUID,
        data_size_bytes: int,
        latency_ms: float,
        success: bool,
        error_message: Optional[str] = None,
    ):
        """Log storage operation for analytics."""
        try:
            operation = StorageOperation(
                operation_id=operation_id,
                operation_type=operation_type,
                tier=tier,
                context_id=context_id,
                data_size_bytes=data_size_bytes,
                latency_ms=latency_ms,
                success=success,
                error_message=error_message,
                wina_optimization_applied=False,  # TODO: Track WINA usage
                optimization_savings_ms=None,
                started_at=datetime.utcnow() - timedelta(milliseconds=latency_ms),
                completed_at=datetime.utcnow(),
                service_name="context_service",
                user_id=None,  # TODO: Extract from context
            )

            # Add to in-memory log
            self.operations_log.append(operation)
            if len(self.operations_log) > self.max_operations_log:
                self.operations_log.pop(0)

            # Log to PostgreSQL if available
            if self.postgres_pool:
                async with self.postgres_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO storage_operations (
                            operation_id, operation_type, tier, context_id, data_size_bytes,
                            latency_ms, success, error_message, wina_optimization_applied,
                            optimization_savings_ms, started_at, completed_at, service_name, user_id
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    """,
                        operation.operation_id,
                        operation.operation_type,
                        operation.tier.value,
                        operation.context_id,
                        operation.data_size_bytes,
                        operation.latency_ms,
                        operation.success,
                        operation.error_message,
                        operation.wina_optimization_applied,
                        operation.optimization_savings_ms,
                        operation.started_at,
                        operation.completed_at,
                        operation.service_name,
                        operation.user_id,
                    )

        except Exception as e:
            logger.debug(f"Failed to log storage operation: {e}")

    async def _intelligent_tiering_loop(self):
        """Background task for intelligent data tiering."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                await self._perform_intelligent_tiering()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in intelligent tiering loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

    async def _cleanup_loop(self):
        """Background task for data cleanup."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._perform_cleanup()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def _perform_intelligent_tiering(self):
        """Perform intelligent data tiering operations."""
        # TODO: Implement intelligent tiering logic
        logger.debug("Performing intelligent tiering")

    async def _perform_cleanup(self):
        """Perform data cleanup operations."""
        # TODO: Implement cleanup logic
        logger.debug("Performing data cleanup")

    async def get_storage_metrics(self) -> dict[StorageTier, StorageMetrics]:
        """Get metrics for all storage tiers."""
        metrics = {}

        # Update L2 metrics from Qdrant
        if self.vector_store:
            metrics[StorageTier.L2_VECTOR] = (
                await self.vector_store.get_storage_metrics()
            )

        # TODO: Update L1 and L3 metrics
        metrics[StorageTier.L1_CACHE] = self.tier_metrics[StorageTier.L1_CACHE]
        metrics[StorageTier.L3_ARCHIVE] = self.tier_metrics[StorageTier.L3_ARCHIVE]

        return metrics

    async def close(self):
        """Close all storage connections."""
        try:
            # Cancel background tasks
            if self.tiering_task:
                self.tiering_task.cancel()
                try:
                    await self.tiering_task
                except asyncio.CancelledError:
                    pass

            if self.cleanup_task:
                self.cleanup_task.cancel()
                try:
                    await self.cleanup_task
                except asyncio.CancelledError:
                    pass

            # Close storage components
            if self.vector_store:
                await self.vector_store.close()

            if self.embedding_service:
                await self.embedding_service.close()

            if self.postgres_pool:
                await self.postgres_pool.close()

            logger.info("Multi-tier storage manager closed")

        except Exception as e:
            logger.error(f"Error closing multi-tier storage manager: {e}")
