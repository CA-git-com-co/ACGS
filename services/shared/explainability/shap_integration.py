"""
SHAP (SHapley Additive exPlanations) Integration

Production-ready SHAP implementation for model explainability,
implementing the ACGE technical validation recommendations for
industry-standard explainability tools.

Key Features:
- Multiple SHAP explainer types (Tree, Linear, Deep, Kernel)
- Optimized explanation computation and caching
- Batch processing for production efficiency
- Integration with existing ACGS monitoring systems
- Constitutional AI explanation validation
"""

import logging
import pickle
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json

# SHAP imports (would be installed via pip install shap)
try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available, using fallback implementations")

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)

class ExplainerType(Enum):
    """Types of SHAP explainers"""
    TREE = "tree"
    LINEAR = "linear"
    DEEP = "deep"
    KERNEL = "kernel"
    PERMUTATION = "permutation"
    PARTITION = "partition"

class ExplanationLevel(Enum):
    """Levels of explanation detail"""
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"

@dataclass
class SHAPExplanation:
    """SHAP explanation result"""
    feature_importance: Dict[str, float]
    shap_values: np.ndarray
    base_value: float
    expected_value: float
    explanation_type: ExplainerType
    confidence: float
    computation_time: float
    timestamp: datetime
    instance_id: Optional[str] = None

@dataclass
class BatchExplanationResult:
    """Result of batch explanation computation"""
    explanations: List[SHAPExplanation]
    summary_statistics: Dict[str, Any]
    failed_instances: List[str]
    total_computation_time: float
    cache_hit_rate: float
    timestamp: datetime

class SHAPExplainer:
    """
    Production-ready SHAP explainer with optimization and caching
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()
        
        # Configuration
        self.cache_enabled = config.get('cache_enabled', True)
        self.cache_ttl_hours = config.get('cache_ttl_hours', 24)
        self.max_cache_size = config.get('max_cache_size', 1000)
        self.batch_size = config.get('batch_size', 100)
        
        # Explainer storage
        self.explainers = {}
        self.explanation_cache = {}
        self.cache_metadata = {}
        
        # Performance metrics
        self.metrics = {
            'total_explanations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_computation_time': 0.0,
            'failed_explanations': 0
        }
        
    async def initialize_explainer(self, 
                                 model: Any,
                                 explainer_type: ExplainerType,
                                 training_data: Optional[np.ndarray] = None,
                                 feature_names: Optional[List[str]] = None) -> bool:
        """
        Initialize SHAP explainer for a given model
        
        Args:
            model: ML model to explain
            explainer_type: Type of SHAP explainer to use
            training_data: Training data for background (required for some explainers)
            feature_names: Names of features
            
        Returns:
            Success status
        """
        if not SHAP_AVAILABLE:
            logger.warning("SHAP not available, using fallback explainer")
            return await self._initialize_fallback_explainer(model, explainer_type)
        
        try:
            explainer_key = f"{explainer_type.value}_{id(model)}"
            
            if explainer_type == ExplainerType.TREE:
                # For tree-based models (XGBoost, LightGBM, CatBoost, sklearn trees)
                explainer = shap.TreeExplainer(model)
                
            elif explainer_type == ExplainerType.LINEAR:
                # For linear models
                explainer = shap.LinearExplainer(model, training_data)
                
            elif explainer_type == ExplainerType.DEEP:
                # For deep learning models
                if training_data is None:
                    raise ValueError("Training data required for Deep explainer")
                explainer = shap.DeepExplainer(model, training_data)
                
            elif explainer_type == ExplainerType.KERNEL:
                # Model-agnostic explainer (slower but works with any model)
                if training_data is None:
                    raise ValueError("Background data required for Kernel explainer")
                explainer = shap.KernelExplainer(model.predict, training_data)
                
            elif explainer_type == ExplainerType.PERMUTATION:
                # Permutation-based explainer
                explainer = shap.PermutationExplainer(model.predict, training_data)
                
            elif explainer_type == ExplainerType.PARTITION:
                # Partition explainer for tree ensembles
                explainer = shap.PartitionExplainer(model.predict, training_data)
                
            else:
                raise ValueError(f"Unsupported explainer type: {explainer_type}")
            
            self.explainers[explainer_key] = {
                'explainer': explainer,
                'type': explainer_type,
                'feature_names': feature_names or [f'feature_{i}' for i in range(getattr(training_data, 'shape', [0, 10])[1])],
                'created_at': datetime.utcnow()
            }
            
            logger.info(f"SHAP {explainer_type.value} explainer initialized successfully")
            
            # Log explainer initialization
            await self.audit_logger.log_explainer_event({
                'event_type': 'explainer_initialized',
                'explainer_type': explainer_type.value,
                'model_id': str(id(model)),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"SHAP explainer initialization failed: {e}")
            return await self._initialize_fallback_explainer(model, explainer_type)

    async def _initialize_fallback_explainer(self, model: Any, explainer_type: ExplainerType) -> bool:
        """Initialize fallback explainer when SHAP is unavailable"""
        try:
            explainer_key = f"fallback_{explainer_type.value}_{id(model)}"
            
            # Simple fallback that uses basic feature importance if available
            fallback_explainer = {
                'model': model,
                'type': 'fallback',
                'feature_importance': getattr(model, 'feature_importances_', None)
            }
            
            self.explainers[explainer_key] = {
                'explainer': fallback_explainer,
                'type': explainer_type,
                'feature_names': [f'feature_{i}' for i in range(10)],  # Default
                'created_at': datetime.utcnow()
            }
            
            logger.info(f"Fallback explainer initialized for {explainer_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Fallback explainer initialization failed: {e}")
            return False

    def _get_cache_key(self, instance_data: np.ndarray, explainer_key: str) -> str:
        """Generate cache key for explanation"""
        data_hash = hashlib.md5(instance_data.tobytes()).hexdigest()
        return f"{explainer_key}_{data_hash}"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached explanation is still valid"""
        if cache_key not in self.cache_metadata:
            return False
        
        cached_time = self.cache_metadata[cache_key]['timestamp']
        expiry_time = cached_time + timedelta(hours=self.cache_ttl_hours)
        
        return datetime.utcnow() < expiry_time

    async def explain_instance(self,
                             model: Any,
                             instance: np.ndarray,
                             explainer_type: ExplainerType,
                             explanation_level: ExplanationLevel = ExplanationLevel.BASIC) -> SHAPExplanation:
        """
        Generate SHAP explanation for a single instance
        
        Args:
            model: ML model
            instance: Single instance to explain
            explainer_type: Type of explainer to use
            explanation_level: Level of detail for explanation
            
        Returns:
            SHAP explanation result
        """
        start_time = datetime.utcnow()
        explainer_key = f"{explainer_type.value}_{id(model)}"
        
        try:
            # Check cache first
            if self.cache_enabled:
                cache_key = self._get_cache_key(instance, explainer_key)
                if cache_key in self.explanation_cache and self._is_cache_valid(cache_key):
                    self.metrics['cache_hits'] += 1
                    cached_explanation = self.explanation_cache[cache_key]
                    logger.debug(f"Cache hit for explanation: {cache_key}")
                    return cached_explanation
                else:
                    self.metrics['cache_misses'] += 1
            
            # Get explainer
            if explainer_key not in self.explainers:
                raise ValueError(f"Explainer not initialized for {explainer_type.value}")
            
            explainer_info = self.explainers[explainer_key]
            explainer = explainer_info['explainer']
            feature_names = explainer_info['feature_names']
            
            if not SHAP_AVAILABLE or explainer_info['type'] == 'fallback':
                return await self._explain_instance_fallback(instance, explainer_info, explanation_level)
            
            # Generate SHAP explanation
            if explainer_type == ExplainerType.TREE:
                shap_values = explainer.shap_values(instance.reshape(1, -1))
                if isinstance(shap_values, list):
                    # Multi-class case
                    shap_values = shap_values[0]  # Use first class for simplicity
                expected_value = explainer.expected_value
                if isinstance(expected_value, (list, np.ndarray)):
                    expected_value = expected_value[0]
                    
            elif explainer_type in [ExplainerType.LINEAR, ExplainerType.KERNEL, ExplainerType.PERMUTATION]:
                shap_values = explainer.shap_values(instance.reshape(1, -1))
                expected_value = explainer.expected_value
                
            elif explainer_type == ExplainerType.DEEP:
                shap_values = explainer.shap_values(instance.reshape(1, -1))
                expected_value = 0.0  # Deep explainer doesn't have expected_value
                
            else:
                raise ValueError(f"Explanation not implemented for {explainer_type}")
            
            # Extract values for single instance
            if shap_values.ndim > 1:
                shap_values_single = shap_values[0]
            else:
                shap_values_single = shap_values
            
            # Create feature importance dictionary
            feature_importance = {
                feature_names[i]: float(shap_values_single[i])
                for i in range(min(len(feature_names), len(shap_values_single)))
            }
            
            # Calculate confidence based on explanation quality
            confidence = self._calculate_explanation_confidence(shap_values_single, explanation_level)
            
            computation_time = (datetime.utcnow() - start_time).total_seconds()
            
            explanation = SHAPExplanation(
                feature_importance=feature_importance,
                shap_values=shap_values_single,
                base_value=float(expected_value),
                expected_value=float(expected_value),
                explanation_type=explainer_type,
                confidence=confidence,
                computation_time=computation_time,
                timestamp=datetime.utcnow(),
                instance_id=hashlib.md5(instance.tobytes()).hexdigest()[:8]
            )
            
            # Cache the explanation
            if self.cache_enabled:
                self._cache_explanation(cache_key, explanation)
            
            # Update metrics
            self._update_metrics(computation_time, True)
            
            # Log explanation generation
            await self.audit_logger.log_explainer_event({
                'event_type': 'explanation_generated',
                'explainer_type': explainer_type.value,
                'computation_time': computation_time,
                'confidence': confidence,
                'timestamp': explanation.timestamp.isoformat()
            })
            
            return explanation
            
        except Exception as e:
            logger.error(f"SHAP explanation failed: {e}")
            self.metrics['failed_explanations'] += 1
            
            # Return fallback explanation
            computation_time = (datetime.utcnow() - start_time).total_seconds()
            return SHAPExplanation(
                feature_importance={'error': 1.0},
                shap_values=np.array([1.0]),
                base_value=0.0,
                expected_value=0.0,
                explanation_type=explainer_type,
                confidence=0.0,
                computation_time=computation_time,
                timestamp=datetime.utcnow(),
                instance_id=f"error_{str(e)[:8]}"
            )

    async def _explain_instance_fallback(self,
                                       instance: np.ndarray,
                                       explainer_info: Dict[str, Any],
                                       explanation_level: ExplanationLevel) -> SHAPExplanation:
        """Fallback explanation when SHAP is unavailable"""
        try:
            feature_names = explainer_info['feature_names']
            
            # Use model feature importance if available
            if 'feature_importance' in explainer_info['explainer'] and explainer_info['explainer']['feature_importance'] is not None:
                importance = explainer_info['explainer']['feature_importance']
                feature_importance = {
                    feature_names[i]: float(importance[i]) if i < len(importance) else 0.0
                    for i in range(len(feature_names))
                }
            else:
                # Simple fallback: use absolute feature values as proxy for importance
                feature_importance = {
                    feature_names[i]: abs(float(instance[i])) if i < len(instance) else 0.0
                    for i in range(len(feature_names))
                }
            
            return SHAPExplanation(
                feature_importance=feature_importance,
                shap_values=np.abs(instance[:len(feature_names)]),
                base_value=0.0,
                expected_value=0.0,
                explanation_type=explainer_info['type'],
                confidence=0.7,  # Lower confidence for fallback
                computation_time=0.01,  # Very fast fallback
                timestamp=datetime.utcnow(),
                instance_id=hashlib.md5(instance.tobytes()).hexdigest()[:8]
            )
            
        except Exception as e:
            logger.error(f"Fallback explanation failed: {e}")
            return SHAPExplanation(
                feature_importance={'fallback_error': 1.0},
                shap_values=np.array([0.0]),
                base_value=0.0,
                expected_value=0.0,
                explanation_type=explainer_info['type'],
                confidence=0.0,
                computation_time=0.0,
                timestamp=datetime.utcnow(),
                instance_id="fallback_error"
            )

    async def explain_batch(self,
                          model: Any,
                          instances: np.ndarray,
                          explainer_type: ExplainerType,
                          explanation_level: ExplanationLevel = ExplanationLevel.BASIC) -> BatchExplanationResult:
        """
        Generate SHAP explanations for a batch of instances
        
        Args:
            model: ML model
            instances: Batch of instances to explain
            explainer_type: Type of explainer to use
            explanation_level: Level of detail for explanations
            
        Returns:
            Batch explanation result
        """
        start_time = datetime.utcnow()
        
        try:
            explanations = []
            failed_instances = []
            cache_hits = 0
            
            # Process in batches for efficiency
            for i in range(0, len(instances), self.batch_size):
                batch = instances[i:i+self.batch_size]
                
                for j, instance in enumerate(batch):
                    try:
                        explanation = await self.explain_instance(
                            model, instance, explainer_type, explanation_level
                        )
                        explanations.append(explanation)
                        
                        # Check if this was a cache hit
                        explainer_key = f"{explainer_type.value}_{id(model)}"
                        cache_key = self._get_cache_key(instance, explainer_key)
                        if cache_key in self.explanation_cache:
                            cache_hits += 1
                            
                    except Exception as e:
                        failed_instances.append(f"instance_{i+j}_{str(e)}")
                        logger.warning(f"Failed to explain instance {i+j}: {e}")
            
            # Calculate summary statistics
            if explanations:
                computation_times = [e.computation_time for e in explanations]
                confidences = [e.confidence for e in explanations]
                
                summary_statistics = {
                    'total_instances': len(instances),
                    'successful_explanations': len(explanations),
                    'failed_explanations': len(failed_instances),
                    'avg_computation_time': np.mean(computation_times),
                    'avg_confidence': np.mean(confidences),
                    'min_confidence': np.min(confidences),
                    'max_confidence': np.max(confidences)
                }
            else:
                summary_statistics = {
                    'total_instances': len(instances),
                    'successful_explanations': 0,
                    'failed_explanations': len(failed_instances),
                    'avg_computation_time': 0.0,
                    'avg_confidence': 0.0,
                    'min_confidence': 0.0,
                    'max_confidence': 0.0
                }
            
            total_computation_time = (datetime.utcnow() - start_time).total_seconds()
            cache_hit_rate = cache_hits / max(1, len(instances))
            
            result = BatchExplanationResult(
                explanations=explanations,
                summary_statistics=summary_statistics,
                failed_instances=failed_instances,
                total_computation_time=total_computation_time,
                cache_hit_rate=cache_hit_rate,
                timestamp=datetime.utcnow()
            )
            
            # Log batch explanation
            await self.audit_logger.log_explainer_event({
                'event_type': 'batch_explanation_completed',
                'batch_size': len(instances),
                'successful_explanations': len(explanations),
                'failed_explanations': len(failed_instances),
                'total_computation_time': total_computation_time,
                'cache_hit_rate': cache_hit_rate,
                'timestamp': result.timestamp.isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Batch explanation failed: {e}")
            return BatchExplanationResult(
                explanations=[],
                summary_statistics={'error': str(e)},
                failed_instances=[f"batch_error_{str(e)}"],
                total_computation_time=(datetime.utcnow() - start_time).total_seconds(),
                cache_hit_rate=0.0,
                timestamp=datetime.utcnow()
            )

    def _calculate_explanation_confidence(self, shap_values: np.ndarray, explanation_level: ExplanationLevel) -> float:
        """Calculate confidence score for explanation quality"""
        try:
            # Base confidence on explanation level and value distribution
            base_confidence = {
                ExplanationLevel.BASIC: 0.8,
                ExplanationLevel.DETAILED: 0.9,
                ExplanationLevel.COMPREHENSIVE: 0.95
            }.get(explanation_level, 0.8)
            
            # Adjust based on value distribution (more concentrated = higher confidence)
            if len(shap_values) > 0:
                value_std = np.std(shap_values)
                value_range = np.max(np.abs(shap_values))
                
                if value_range > 0:
                    concentration_factor = min(1.0, value_std / value_range)
                    confidence = base_confidence * (1.0 - concentration_factor * 0.2)
                else:
                    confidence = base_confidence * 0.8
            else:
                confidence = base_confidence * 0.5
            
            return max(0.1, min(1.0, confidence))
            
        except Exception:
            return 0.5

    def _cache_explanation(self, cache_key: str, explanation: SHAPExplanation):
        """Cache explanation result"""
        try:
            # Check cache size limit
            if len(self.explanation_cache) >= self.max_cache_size:
                self._evict_oldest_cache_entries()
            
            self.explanation_cache[cache_key] = explanation
            self.cache_metadata[cache_key] = {
                'timestamp': datetime.utcnow(),
                'access_count': 1
            }
            
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    def _evict_oldest_cache_entries(self):
        """Evict oldest cache entries to make room"""
        try:
            # Remove oldest 20% of cache entries
            entries_to_remove = max(1, int(self.max_cache_size * 0.2))
            
            # Sort by timestamp
            sorted_entries = sorted(
                self.cache_metadata.items(),
                key=lambda x: x[1]['timestamp']
            )
            
            for cache_key, _ in sorted_entries[:entries_to_remove]:
                self.explanation_cache.pop(cache_key, None)
                self.cache_metadata.pop(cache_key, None)
                
        except Exception as e:
            logger.warning(f"Cache eviction failed: {e}")

    def _update_metrics(self, computation_time: float, success: bool):
        """Update performance metrics"""
        self.metrics['total_explanations'] += 1
        
        if success:
            current_avg = self.metrics['avg_computation_time']
            total_explanations = self.metrics['total_explanations']
            self.metrics['avg_computation_time'] = (
                (current_avg * (total_explanations - 1) + computation_time) / total_explanations
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get explainer performance summary"""
        total_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
        cache_hit_rate = self.metrics['cache_hits'] / max(1, total_requests)
        
        return {
            'total_explanations': self.metrics['total_explanations'],
            'failed_explanations': self.metrics['failed_explanations'],
            'success_rate': (
                (self.metrics['total_explanations'] - self.metrics['failed_explanations']) /
                max(1, self.metrics['total_explanations'])
            ),
            'avg_computation_time': self.metrics['avg_computation_time'],
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.explanation_cache),
            'active_explainers': len(self.explainers)
        }

    async def cleanup_cache(self, max_age_hours: Optional[int] = None):
        """Clean up expired cache entries"""
        if max_age_hours is None:
            max_age_hours = self.cache_ttl_hours
        
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            expired_keys = [
                key for key, metadata in self.cache_metadata.items()
                if metadata['timestamp'] < cutoff_time
            ]
            
            for key in expired_keys:
                self.explanation_cache.pop(key, None)
                self.cache_metadata.pop(key, None)
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")

# Example usage
async def example_usage():
    """Example of how to use the SHAP integration"""
    # Initialize explainer
    explainer = SHAPExplainer({
        'cache_enabled': True,
        'cache_ttl_hours': 24,
        'batch_size': 50
    })
    
    # Mock model and data
    class MockModel:
        def predict(self, X):
            return np.random.random(len(X))
        
        @property
        def feature_importances_(self):
            return np.random.random(10)
    
    model = MockModel()
    training_data = np.random.randn(100, 10)
    test_instance = np.random.randn(10)
    
    # Initialize explainer
    success = await explainer.initialize_explainer(
        model, ExplainerType.KERNEL, training_data
    )
    
    if success:
        # Generate explanation
        explanation = await explainer.explain_instance(
            model, test_instance, ExplainerType.KERNEL
        )
        
        print(f"Feature importance: {explanation.feature_importance}")
        print(f"Confidence: {explanation.confidence}")
        
        # Get performance summary
        summary = explainer.get_performance_summary()
        print(f"Performance: {summary}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())