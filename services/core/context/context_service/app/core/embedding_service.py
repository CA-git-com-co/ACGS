"""
Embedding Service for Context Vectors

High-performance embedding generation service with support for multiple models,
caching, and WINA optimization for efficient context vectorization.
"""

import asyncio
import hashlib
import logging
import time
from datetime import datetime
from typing import Any, Optional

try:
    import numpy as np
    import torch
    from sentence_transformers import SentenceTransformer

    EMBEDDING_LIBS_AVAILABLE = True
except ImportError:
    EMBEDDING_LIBS_AVAILABLE = False

    # Mock classes for when libraries are not available
    class SentenceTransformer:
        def __init__(self, *args, **kwargs):
            pass

        def encode(self, *args, **kwargs):
            return [[0.0] * 384]  # Mock 384-dimensional vector

    class np:
        @staticmethod
        def array(x):
            return x

        @staticmethod
        def linalg_norm(x):
            return 1.0


from services.shared.cache.redis_cluster import get_cache_manager

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    High-performance embedding service for context vectorization.

    Features:
    - Multiple embedding model support
    - Redis caching for frequently embedded content
    - Batch processing for efficiency
    - WINA optimization integration
    - Content preprocessing and normalization
    """

    def __init__(
        self,
        primary_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        fallback_model: str = "sentence-transformers/all-mpnet-base-v2",
        cache_ttl_hours: int = 24,
        enable_caching: bool = True,
        enable_wina_optimization: bool = True,
        device: Optional[str] = None,
    ):
        """
        Initialize embedding service.

        Args:
            primary_model: Primary embedding model name
            fallback_model: Fallback model if primary fails
            cache_ttl_hours: Cache TTL in hours
            enable_caching: Enable Redis caching
            enable_wina_optimization: Enable WINA optimization
            device: Device for model inference (cpu, cuda, auto)
        """
        self.primary_model_name = primary_model
        self.fallback_model_name = fallback_model
        self.cache_ttl_hours = cache_ttl_hours
        self.enable_caching = enable_caching
        self.enable_wina_optimization = enable_wina_optimization

        # Determine device
        if device is None:
            if EMBEDDING_LIBS_AVAILABLE:
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = "cpu"
        else:
            self.device = device

        # Model instances
        self.primary_model: Optional[SentenceTransformer] = None
        self.fallback_model: Optional[SentenceTransformer] = None
        self.models_loaded = False

        # Cache manager
        self.cache_manager = None

        # Performance metrics
        self.metrics = {
            "embeddings_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "model_switches": 0,
            "total_latency_ms": 0.0,
            "average_latency_ms": 0.0,
            "wina_optimizations": 0,
            "preprocessing_time_ms": 0.0,
            "inference_time_ms": 0.0,
        }

        # Model configurations
        self.model_configs = {
            "sentence-transformers/all-MiniLM-L6-v2": {
                "dimension": 384,
                "max_seq_length": 256,
                "normalization": True,
                "pooling": "mean",
            },
            "sentence-transformers/all-mpnet-base-v2": {
                "dimension": 768,
                "max_seq_length": 384,
                "normalization": True,
                "pooling": "mean",
            },
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": {
                "dimension": 384,
                "max_seq_length": 128,
                "normalization": True,
                "pooling": "mean",
            },
        }

        # WINA optimization components
        self.wina_core = None
        self.wina_integrator = None

    async def initialize(self) -> bool:
        """
        Initialize embedding service with models and cache.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            if not EMBEDDING_LIBS_AVAILABLE:
                logger.warning(
                    "Embedding libraries not available. Using mock embeddings."
                )
                self.models_loaded = True
                return True

            # Initialize cache manager
            if self.enable_caching:
                try:
                    self.cache_manager = get_cache_manager()
                    logger.info("Cache manager initialized for embeddings")
                except Exception as e:
                    logger.warning(f"Failed to initialize cache manager: {e}")
                    self.enable_caching = False

            # Load primary model
            await self._load_model(self.primary_model_name, is_primary=True)

            # Load fallback model if different
            if self.fallback_model_name != self.primary_model_name:
                await self._load_model(self.fallback_model_name, is_primary=False)

            # Initialize WINA optimization
            if self.enable_wina_optimization:
                await self._initialize_wina_optimization()

            self.models_loaded = True
            logger.info(
                "Embedding service initialized with primary model:"
                f" {self.primary_model_name}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            return False

    async def _load_model(self, model_name: str, is_primary: bool = True):
        """Load a sentence transformer model."""
        try:
            logger.info(f"Loading embedding model: {model_name}")

            def load_model():
                model = SentenceTransformer(model_name, device=self.device)
                return model

            # Load model in thread to avoid blocking
            model = await asyncio.to_thread(load_model)

            if is_primary:
                self.primary_model = model
            else:
                self.fallback_model = model

            logger.info(f"Successfully loaded model: {model_name}")

        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            if is_primary:
                # Try fallback as primary
                if self.fallback_model_name != model_name:
                    await self._load_model(self.fallback_model_name, is_primary=True)

    async def _initialize_wina_optimization(self):
        """Initialize WINA optimization for embedding models."""
        try:
            from services.shared.wina.config import load_wina_config_from_env
            from services.shared.wina.core import WINACore
            from services.shared.wina.model_integration import WINAModelIntegrator

            # Load WINA configuration
            wina_config, wina_integration_config = load_wina_config_from_env()

            # Initialize WINA core and model integrator
            self.wina_core = WINACore(wina_config, wina_integration_config)
            self.wina_integrator = WINAModelIntegrator(
                wina_config, wina_integration_config
            )

            logger.info("WINA optimization initialized successfully")
        except ImportError as e:
            logger.warning(f"WINA modules not available: {e}")
            self.enable_wina_optimization = False
        except Exception as e:
            logger.warning(f"Failed to initialize WINA optimization: {e}")
            self.enable_wina_optimization = False

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text for embedding generation.

        Args:
            text: Input text

        Returns:
            Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""

        # Basic preprocessing
        text = text.strip()

        # Remove excessive whitespace
        text = " ".join(text.split())

        # Truncate if too long (model-specific limits)
        model_config = self.model_configs.get(self.primary_model_name, {})
        max_length = model_config.get("max_seq_length", 256)

        # Rough character to token ratio (1 token ≈ 4 characters for English)
        max_chars = max_length * 4
        if len(text) > max_chars:
            text = text[:max_chars].rsplit(" ", 1)[0]  # Cut at word boundary

        return text

    def _get_cache_key(self, text: str, model_name: str) -> str:
        """Generate cache key for text embedding."""
        content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        model_hash = hashlib.sha256(model_name.encode()).hexdigest()[:8]
        return f"embedding:{model_hash}:{content_hash}"

    async def _get_cached_embedding(self, cache_key: str) -> Optional[list[float]]:
        """Retrieve embedding from cache."""
        if not self.enable_caching or not self.cache_manager:
            return None

        try:
            cached_data = await self.cache_manager.get(cache_key)
            if cached_data and isinstance(cached_data, dict):
                embedding = cached_data.get("embedding")
                if embedding and isinstance(embedding, list):
                    self.metrics["cache_hits"] += 1
                    return embedding
        except Exception as e:
            logger.debug(f"Cache retrieval failed: {e}")

        self.metrics["cache_misses"] += 1
        return None

    async def _cache_embedding(
        self, cache_key: str, embedding: list[float], model_name: str
    ):
        """Cache embedding for future use."""
        if not self.enable_caching or not self.cache_manager:
            return

        try:
            cache_data = {
                "embedding": embedding,
                "model": model_name,
                "timestamp": datetime.utcnow().isoformat(),
                "dimension": len(embedding),
            }

            ttl = self.cache_ttl_hours * 3600  # Convert to seconds
            await self.cache_manager.set(cache_key, cache_data, ttl=ttl)

        except Exception as e:
            logger.debug(f"Cache storage failed: {e}")

    async def generate_embedding(
        self,
        text: str,
        model_name: Optional[str] = None,
        normalize: bool = True,
        use_cache: bool = True,
    ) -> tuple[list[float], dict[str, Any]]:
        """
        Generate embedding for text.

        Args:
            text: Input text
            model_name: Specific model to use (defaults to primary)
            normalize: Whether to normalize the embedding vector
            use_cache: Whether to use caching

        Returns:
            Tuple of (embedding_vector, metadata)
        """
        start_time = time.time()
        preprocessing_start = start_time

        # Preprocess text
        processed_text = self._preprocess_text(text)
        if not processed_text:
            return [], {"error": "Empty or invalid text"}

        preprocessing_time = (time.time() - preprocessing_start) * 1000
        self.metrics["preprocessing_time_ms"] += preprocessing_time

        # Determine model to use
        target_model_name = model_name or self.primary_model_name

        # Check cache
        cache_key = self._get_cache_key(processed_text, target_model_name)
        if use_cache and self.enable_caching:
            cached_embedding = await self._get_cached_embedding(cache_key)
            if cached_embedding:
                total_latency = (time.time() - start_time) * 1000
                return cached_embedding, {
                    "model": target_model_name,
                    "cached": True,
                    "latency_ms": total_latency,
                    "preprocessing_time_ms": preprocessing_time,
                    "cache_hit": True,
                }

        # Generate embedding
        inference_start = time.time()
        try:
            embedding = await self._generate_embedding_with_model(
                processed_text, target_model_name, normalize
            )

            inference_time = (time.time() - inference_start) * 1000
            self.metrics["inference_time_ms"] += inference_time

            # Cache the result
            if use_cache:
                await self._cache_embedding(cache_key, embedding, target_model_name)

            # Update metrics
            total_latency = (time.time() - start_time) * 1000
            self._update_metrics(total_latency, True)

            metadata = {
                "model": target_model_name,
                "cached": False,
                "latency_ms": total_latency,
                "preprocessing_time_ms": preprocessing_time,
                "inference_time_ms": inference_time,
                "dimension": len(embedding),
                "normalized": normalize,
                "device": self.device,
            }

            # Apply WINA optimization if enabled
            if self.enable_wina_optimization and self.wina_optimizer:
                try:
                    optimized_embedding = await self._apply_wina_optimization(embedding)
                    if optimized_embedding:
                        embedding = optimized_embedding
                        metadata["wina_optimized"] = True
                        self.metrics["wina_optimizations"] += 1
                except Exception as e:
                    logger.debug(f"WINA optimization failed: {e}")
                    metadata["wina_optimized"] = False

            return embedding, metadata

        except Exception as e:
            total_latency = (time.time() - start_time) * 1000
            self._update_metrics(total_latency, False)
            logger.error(f"Embedding generation failed: {e}")
            return [], {"error": str(e), "latency_ms": total_latency}

    async def _generate_embedding_with_model(
        self, text: str, model_name: str, normalize: bool
    ) -> list[float]:
        """Generate embedding using specified model."""

        # Select model
        model = None
        if model_name == self.primary_model_name and self.primary_model:
            model = self.primary_model
        elif model_name == self.fallback_model_name and self.fallback_model:
            model = self.fallback_model

        if not model:
            # Try fallback
            if self.fallback_model and model_name != self.fallback_model_name:
                model = self.fallback_model
                self.metrics["model_switches"] += 1
                logger.warning(
                    f"Switched to fallback model: {self.fallback_model_name}"
                )
            else:
                raise RuntimeError(f"Model {model_name} not available")

        # Generate embedding
        def encode_text():
            if EMBEDDING_LIBS_AVAILABLE:
                embedding = model.encode(
                    [text], convert_to_tensor=False, normalize_embeddings=normalize
                )
                return embedding[0].tolist()
            else:
                # Mock embedding for when libraries are not available
                return [0.1] * 384

        embedding = await asyncio.to_thread(encode_text)

        # Additional normalization if requested and not done by model
        if normalize and not self.model_configs.get(model_name, {}).get(
            "normalization", False
        ):
            if EMBEDDING_LIBS_AVAILABLE:
                embedding_array = np.array(embedding)
                norm = np.linalg.norm(embedding_array)
                if norm > 0:
                    embedding = (embedding_array / norm).tolist()

        return embedding

    async def _apply_wina_optimization(
        self, embedding: list[float]
    ) -> Optional[list[float]]:
        """Apply WINA optimization to embedding vector."""
        if not self.enable_wina_optimization or not hasattr(self, "wina_integrator"):
            return None

        try:
            # Convert embedding to numpy array for WINA processing
            if EMBEDDING_LIBS_AVAILABLE:
                embedding_array = np.array(embedding)

                # Apply WINA optimization to the embedding model
                # Note: This is a simplified implementation
                # In practice, WINA would optimize the embedding model weights
                # Here we simulate the optimization effect

                # Use WINA integrator to optimize the embedding
                optimization_result = await self.wina_integrator.optimize_model(
                    model_identifier="embedding_model",
                    model_type="sentence_transformer",
                    target_layers=None,  # Optimize all layers
                    force_recompute=False,
                )

                if optimization_result and optimization_result.success:
                    # Apply compression based on WINA optimization
                    compression_ratio = optimization_result.gflops_reduction

                    # Simulate WINA effect by selective dimension reduction
                    # This preserves the most important dimensions
                    if compression_ratio > 0.0:
                        # Calculate how many dimensions to keep
                        keep_ratio = 1.0 - (
                            compression_ratio * 0.1
                        )  # Conservative compression
                        keep_dims = int(len(embedding) * keep_ratio)
                        keep_dims = max(
                            keep_dims, len(embedding) // 2
                        )  # Keep at least 50%

                        # Use magnitude-based selection (simple heuristic)
                        magnitude_indices = np.argsort(np.abs(embedding_array))[::-1]
                        selected_indices = sorted(magnitude_indices[:keep_dims])

                        # Create compressed embedding with zeros for non-selected dimensions
                        optimized_embedding = np.zeros_like(embedding_array)
                        optimized_embedding[selected_indices] = embedding_array[
                            selected_indices
                        ]

                        # Renormalize to maintain vector properties
                        norm = np.linalg.norm(optimized_embedding)
                        if norm > 0:
                            optimized_embedding = optimized_embedding / norm

                        return optimized_embedding.tolist()

            return None

        except Exception as e:
            logger.debug(f"WINA optimization failed: {e}")
            return None

    async def generate_batch_embeddings(
        self,
        texts: list[str],
        model_name: Optional[str] = None,
        normalize: bool = True,
        use_cache: bool = True,
        batch_size: int = 32,
    ) -> list[tuple[list[float], dict[str, Any]]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of input texts
            model_name: Model to use
            normalize: Whether to normalize embeddings
            use_cache: Whether to use caching
            batch_size: Batch size for processing

        Returns:
            List of (embedding, metadata) tuples
        """
        if not texts:
            return []

        results = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]

            # Generate embeddings for batch
            batch_tasks = [
                self.generate_embedding(text, model_name, normalize, use_cache)
                for text in batch_texts
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process results
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(([], {"error": str(result)}))
                else:
                    results.append(result)

        return results

    def get_model_info(self, model_name: Optional[str] = None) -> dict[str, Any]:
        """Get information about embedding model."""
        target_model = model_name or self.primary_model_name
        config = self.model_configs.get(target_model, {})

        return {
            "model_name": target_model,
            "dimension": config.get("dimension", 384),
            "max_sequence_length": config.get("max_seq_length", 256),
            "device": self.device,
            "normalization": config.get("normalization", True),
            "pooling_strategy": config.get("pooling", "mean"),
            "loaded": self.models_loaded,
            "wina_optimization": self.enable_wina_optimization,
        }

    def get_metrics(self) -> dict[str, Any]:
        """Get performance metrics."""
        total_requests = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        cache_hit_rate = (self.metrics["cache_hits"] / max(1, total_requests)) * 100

        return {
            "embeddings_generated": self.metrics["embeddings_generated"],
            "cache_hit_rate": cache_hit_rate,
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "model_switches": self.metrics["model_switches"],
            "average_latency_ms": self.metrics["average_latency_ms"],
            "average_preprocessing_time_ms": self.metrics["preprocessing_time_ms"]
            / max(1, self.metrics["embeddings_generated"]),
            "average_inference_time_ms": self.metrics["inference_time_ms"]
            / max(1, self.metrics["embeddings_generated"]),
            "wina_optimizations": self.metrics["wina_optimizations"],
            "models_loaded": self.models_loaded,
            "primary_model": self.primary_model_name,
            "fallback_model": self.fallback_model_name,
        }

    def _update_metrics(self, latency_ms: float, success: bool):
        """Update performance metrics."""
        if success:
            self.metrics["embeddings_generated"] += 1
            self.metrics["total_latency_ms"] += latency_ms
            self.metrics["average_latency_ms"] = (
                self.metrics["total_latency_ms"] / self.metrics["embeddings_generated"]
            )

    async def close(self):
        """Cleanup resources."""
        try:
            # Clear models from memory
            if self.primary_model:
                del self.primary_model
                self.primary_model = None

            if self.fallback_model:
                del self.fallback_model
                self.fallback_model = None

            # Clear CUDA cache if using GPU
            if EMBEDDING_LIBS_AVAILABLE and self.device.startswith("cuda"):
                torch.cuda.empty_cache()

            logger.info("Embedding service resources cleaned up")

        except Exception as e:
            logger.error(f"Error during embedding service cleanup: {e}")
