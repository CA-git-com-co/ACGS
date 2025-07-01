#!/usr/bin/env python3
"""
ML-Based Routing Optimizer for ACGS-PGP Multimodal AI Service

This module implements machine learning algorithms to optimize model selection
based on historical performance data and request patterns.

Features:
- Historical performance tracking
- Request pattern analysis
- ML-based model selection
- Performance prediction
- Adaptive routing optimization

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

from services.shared.ai_types import ModelType, MultimodalRequest, RequestType, ContentType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Performance metric for a model on a specific request."""
    model_type: ModelType
    request_type: RequestType
    content_type: ContentType
    response_time_ms: float
    token_count: int
    cost_estimate: float
    quality_score: float
    constitutional_compliance: bool
    timestamp: datetime
    content_length: int
    cache_hit: bool


@dataclass
class RequestFeatures:
    """Feature vector for ML model prediction."""
    request_type_encoded: int
    content_type_encoded: int
    content_length: int
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    historical_avg_response_time: float
    historical_success_rate: float


class MLRoutingOptimizer:
    """ML-based routing optimizer for intelligent model selection."""
    
    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.performance_history: List[PerformanceMetric] = []
        self.models = {}
        self.scalers = {}
        self.model_file_path = "data/ml_routing_models.joblib"
        self.history_file_path = "data/performance_history.json"
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize ML models for each metric
        self._initialize_models()
        
        # Load existing data
        self._load_performance_history()
        self._load_ml_models()
    
    def _initialize_models(self):
        """Initialize ML models for different performance metrics."""
        self.models = {
            'response_time': RandomForestRegressor(n_estimators=100, random_state=42),
            'cost': RandomForestRegressor(n_estimators=100, random_state=42),
            'quality': RandomForestRegressor(n_estimators=100, random_state=42),
            'compliance': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        self.scalers = {
            'response_time': StandardScaler(),
            'cost': StandardScaler(),
            'quality': StandardScaler(),
            'compliance': StandardScaler()
        }
    
    def _encode_request_type(self, request_type: RequestType) -> int:
        """Encode request type as integer."""
        encoding = {
            RequestType.QUICK_ANALYSIS: 0,
            RequestType.DETAILED_ANALYSIS: 1,
            RequestType.CONSTITUTIONAL_VALIDATION: 2,
            RequestType.MULTIMODAL_PROCESSING: 3
        }
        return encoding.get(request_type, 0)
    
    def _encode_content_type(self, content_type: ContentType) -> int:
        """Encode content type as integer."""
        encoding = {
            ContentType.TEXT_ONLY: 0,
            ContentType.IMAGE_ONLY: 1,
            ContentType.TEXT_AND_IMAGE: 2
        }
        return encoding.get(content_type, 0)
    
    def _extract_features(self, request: MultimodalRequest) -> RequestFeatures:
        """Extract features from a request for ML prediction."""
        now = datetime.now()
        content_length = len(request.text_content or "") + (1000 if request.image_url or request.image_data else 0)
        
        # Calculate historical metrics
        historical_metrics = self._get_historical_metrics(request.request_type, request.content_type)
        
        return RequestFeatures(
            request_type_encoded=self._encode_request_type(request.request_type),
            content_type_encoded=self._encode_content_type(request.content_type),
            content_length=content_length,
            hour_of_day=now.hour,
            day_of_week=now.weekday(),
            is_weekend=now.weekday() >= 5,
            historical_avg_response_time=historical_metrics['avg_response_time'],
            historical_success_rate=historical_metrics['success_rate']
        )
    
    def _get_historical_metrics(self, request_type: RequestType, content_type: ContentType) -> Dict[str, float]:
        """Get historical performance metrics for similar requests."""
        relevant_metrics = [
            m for m in self.performance_history
            if m.request_type == request_type and m.content_type == content_type
            and m.timestamp > datetime.now() - timedelta(days=30)
        ]
        
        if not relevant_metrics:
            return {'avg_response_time': 1000.0, 'success_rate': 0.95}
        
        avg_response_time = np.mean([m.response_time_ms for m in relevant_metrics])
        success_rate = np.mean([1.0 if m.constitutional_compliance else 0.0 for m in relevant_metrics])
        
        return {
            'avg_response_time': avg_response_time,
            'success_rate': success_rate
        }
    
    def record_performance(self, request: MultimodalRequest, model_type: ModelType, 
                          response_time_ms: float, token_count: int, cost_estimate: float,
                          quality_score: float, constitutional_compliance: bool, cache_hit: bool):
        """Record performance metric for ML training."""
        metric = PerformanceMetric(
            model_type=model_type,
            request_type=request.request_type,
            content_type=request.content_type,
            response_time_ms=response_time_ms,
            token_count=token_count,
            cost_estimate=cost_estimate,
            quality_score=quality_score,
            constitutional_compliance=constitutional_compliance,
            timestamp=datetime.now(),
            content_length=len(request.text_content or "") + (1000 if request.image_url or request.image_data else 0),
            cache_hit=cache_hit
        )
        
        self.performance_history.append(metric)
        
        # Keep only last 10000 records
        if len(self.performance_history) > 10000:
            self.performance_history = self.performance_history[-10000:]
        
        # Save to disk periodically
        if len(self.performance_history) % 100 == 0:
            self._save_performance_history()
    
    def predict_performance(self, request: MultimodalRequest, model_type: ModelType) -> Dict[str, float]:
        """Predict performance metrics for a request-model combination."""
        features = self._extract_features(request)
        feature_vector = np.array([
            features.request_type_encoded,
            features.content_type_encoded,
            features.content_length,
            features.hour_of_day,
            features.day_of_week,
            int(features.is_weekend),
            features.historical_avg_response_time,
            features.historical_success_rate,
            self._encode_model_type(model_type)
        ]).reshape(1, -1)
        
        predictions = {}
        
        # If models are trained, use them for prediction
        if self._models_trained():
            try:
                for metric_name, model in self.models.items():
                    scaled_features = self.scalers[metric_name].transform(feature_vector)
                    prediction = model.predict(scaled_features)[0]
                    predictions[metric_name] = max(0, prediction)  # Ensure non-negative
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}, using fallback")
                predictions = self._fallback_prediction(request, model_type)
        else:
            predictions = self._fallback_prediction(request, model_type)
        
        return predictions
    
    def _encode_model_type(self, model_type: ModelType) -> int:
        """Encode model type as integer."""
        encoding = {
            ModelType.FLASH_LITE: 0,
            ModelType.FLASH_FULL: 1,
            ModelType.DEEPSEEK_R1: 2
        }
        return encoding.get(model_type, 0)
    
    def _fallback_prediction(self, request: MultimodalRequest, model_type: ModelType) -> Dict[str, float]:
        """Fallback prediction based on heuristics."""
        base_predictions = {
            ModelType.FLASH_LITE: {
                'response_time': 800.0,
                'cost': 0.001,
                'quality': 0.85,
                'compliance': 0.95
            },
            ModelType.FLASH_FULL: {
                'response_time': 1200.0,
                'cost': 0.003,
                'quality': 0.92,
                'compliance': 0.97
            },
            ModelType.DEEPSEEK_R1: {
                'response_time': 1500.0,
                'cost': 0.0008,  # 74% cost reduction
                'quality': 0.90,
                'compliance': 0.96
            }
        }
        
        # Adjust based on request complexity
        content_length = len(request.text_content or "")
        complexity_factor = min(2.0, 1.0 + content_length / 1000.0)
        
        predictions = base_predictions.get(model_type, base_predictions[ModelType.FLASH_LITE]).copy()
        predictions['response_time'] *= complexity_factor
        predictions['cost'] *= complexity_factor
        
        return predictions
    
    def select_optimal_model(self, request: MultimodalRequest, 
                           available_models: List[ModelType]) -> Tuple[ModelType, Dict[str, float]]:
        """Select the optimal model based on ML predictions."""
        best_model = None
        best_score = float('-inf')
        best_predictions = {}
        
        for model_type in available_models:
            predictions = self.predict_performance(request, model_type)
            
            # Calculate composite score (lower is better for response_time and cost)
            score = (
                -predictions['response_time'] / 1000.0 +  # Normalize and invert
                -predictions['cost'] * 1000.0 +           # Normalize and invert
                predictions['quality'] * 2.0 +            # Quality weight
                predictions['compliance'] * 3.0           # Compliance weight (highest)
            )
            
            if score > best_score:
                best_score = score
                best_model = model_type
                best_predictions = predictions
        
        return best_model or available_models[0], best_predictions
    
    def train_models(self):
        """Train ML models on historical performance data."""
        if len(self.performance_history) < 50:
            logger.info("Insufficient data for ML training (need at least 50 samples)")
            return
        
        logger.info(f"Training ML models on {len(self.performance_history)} samples")
        
        # Prepare training data
        X = []
        y = {
            'response_time': [],
            'cost': [],
            'quality': [],
            'compliance': []
        }
        
        for metric in self.performance_history:
            features = [
                self._encode_request_type(metric.request_type),
                self._encode_content_type(metric.content_type),
                metric.content_length,
                metric.timestamp.hour,
                metric.timestamp.weekday(),
                int(metric.timestamp.weekday() >= 5),
                0.0,  # historical_avg_response_time (placeholder)
                0.0,  # historical_success_rate (placeholder)
                self._encode_model_type(metric.model_type)
            ]
            
            X.append(features)
            y['response_time'].append(metric.response_time_ms)
            y['cost'].append(metric.cost_estimate)
            y['quality'].append(metric.quality_score)
            y['compliance'].append(1.0 if metric.constitutional_compliance else 0.0)
        
        X = np.array(X)
        
        # Train models
        for metric_name in y.keys():
            try:
                y_values = np.array(y[metric_name])
                
                # Scale features
                X_scaled = self.scalers[metric_name].fit_transform(X)
                
                # Train model
                self.models[metric_name].fit(X_scaled, y_values)
                
                logger.info(f"Trained {metric_name} model with score: {self.models[metric_name].score(X_scaled, y_values):.3f}")
                
            except Exception as e:
                logger.error(f"Failed to train {metric_name} model: {e}")
        
        # Save trained models
        self._save_ml_models()
    
    def _models_trained(self) -> bool:
        """Check if ML models are trained."""
        try:
            # Check if all models have been fitted
            for model in self.models.values():
                if not hasattr(model, 'feature_importances_'):
                    return False
            return True
        except:
            return False
    
    def _save_performance_history(self):
        """Save performance history to disk."""
        try:
            data = []
            for metric in self.performance_history:
                metric_dict = asdict(metric)
                metric_dict['model_type'] = metric.model_type.value
                metric_dict['request_type'] = metric.request_type.value
                metric_dict['content_type'] = metric.content_type.value
                metric_dict['timestamp'] = metric.timestamp.isoformat()
                data.append(metric_dict)
            
            with open(self.history_file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save performance history: {e}")
    
    def _load_performance_history(self):
        """Load performance history from disk."""
        try:
            if os.path.exists(self.history_file_path):
                with open(self.history_file_path, 'r') as f:
                    data = json.load(f)
                
                self.performance_history = []
                for item in data:
                    metric = PerformanceMetric(
                        model_type=ModelType(item['model_type']),
                        request_type=RequestType(item['request_type']),
                        content_type=ContentType(item['content_type']),
                        response_time_ms=item['response_time_ms'],
                        token_count=item['token_count'],
                        cost_estimate=item['cost_estimate'],
                        quality_score=item['quality_score'],
                        constitutional_compliance=item['constitutional_compliance'],
                        timestamp=datetime.fromisoformat(item['timestamp']),
                        content_length=item['content_length'],
                        cache_hit=item['cache_hit']
                    )
                    self.performance_history.append(metric)
                
                logger.info(f"Loaded {len(self.performance_history)} performance records")
                
        except Exception as e:
            logger.error(f"Failed to load performance history: {e}")
    
    def _save_ml_models(self):
        """Save trained ML models to disk."""
        try:
            model_data = {
                'models': self.models,
                'scalers': self.scalers,
                'constitutional_hash': self.constitutional_hash
            }
            joblib.dump(model_data, self.model_file_path)
            logger.info("ML models saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save ML models: {e}")
    
    def _load_ml_models(self):
        """Load trained ML models from disk."""
        try:
            if os.path.exists(self.model_file_path):
                model_data = joblib.load(self.model_file_path)
                self.models = model_data['models']
                self.scalers = model_data['scalers']
                logger.info("ML models loaded successfully")
            else:
                logger.info(
                    "ML model file not found. Run 'python scripts/generate_ml_routing_models.py' to create it."
                )
                
        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics and insights."""
        if not self.performance_history:
            return {"message": "No performance data available"}
        
        # Calculate metrics by model
        model_stats = {}
        for model_type in ModelType:
            model_metrics = [m for m in self.performance_history if m.model_type == model_type]
            if model_metrics:
                model_stats[model_type.value] = {
                    'count': len(model_metrics),
                    'avg_response_time': np.mean([m.response_time_ms for m in model_metrics]),
                    'avg_cost': np.mean([m.cost_estimate for m in model_metrics]),
                    'avg_quality': np.mean([m.quality_score for m in model_metrics]),
                    'compliance_rate': np.mean([1.0 if m.constitutional_compliance else 0.0 for m in model_metrics])
                }
        
        return {
            'total_requests': len(self.performance_history),
            'models_trained': self._models_trained(),
            'model_statistics': model_stats,
            'constitutional_hash': self.constitutional_hash
        }


# Global instance
_ml_optimizer = None


async def get_ml_optimizer() -> MLRoutingOptimizer:
    """Get the global ML routing optimizer instance."""
    global _ml_optimizer
    if _ml_optimizer is None:
        _ml_optimizer = MLRoutingOptimizer()
    return _ml_optimizer
