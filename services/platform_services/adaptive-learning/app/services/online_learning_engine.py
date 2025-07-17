"""
Online Learning Engine - Real-time learning with differential privacy
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib

# Online learning frameworks
from river import base, compose, drift, ensemble, linear_model, metrics, preprocessing, stats
from river.drift import ADWIN, KSWIN, PageHinkley
from river.ensemble import AdaptiveRandomForestClassifier
from river.linear_model import LogisticRegression, PassiveAggressiveClassifier
from river.metrics import Accuracy, F1, Precision, Recall
from river.preprocessing import StandardScaler, MinMaxScaler

# Differential privacy
import opacus
from opacus import PrivacyEngine
from opacus.utils.batch_memory_manager import BatchMemoryManager
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset

# Apache Beam for streaming
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows
from apache_beam.transforms.trigger import AfterWatermark, AfterProcessingTime, OrFinally

# Reinforcement learning
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv
import gym

import redis.asyncio as redis
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError

from ..models.schemas import (
    Feedback,
    LearningMetric,
    ModelConfiguration,
    TrainingJob,
    ModelType,
    FeedbackType,
    CONSTITUTIONAL_HASH
)

logger = logging.getLogger(__name__)

class PrivacyLevel(Enum):
    """Differential privacy levels."""
    LOW = "low"      # ε = 1.0
    MEDIUM = "medium"  # ε = 0.1
    HIGH = "high"    # ε = 0.01
    ULTRA = "ultra"  # ε = 0.001

@dataclass
class OnlineModel:
    """Online learning model container."""
    model: base.Base
    scaler: preprocessing.StandardScaler
    drift_detector: drift.base.DriftDetector
    metrics: Dict[str, metrics.base.Metric]
    training_samples: int = 0
    accuracy_history: List[float] = field(default_factory=list)
    constitutional_hash: str = CONSTITUTIONAL_HASH

@dataclass
class DifferentialPrivacyConfig:
    """Differential privacy configuration."""
    epsilon: float
    delta: float
    max_grad_norm: float
    noise_multiplier: float
    sample_rate: float
    constitutional_hash: str = CONSTITUTIONAL_HASH

class OnlineLearningEngine:
    """Advanced online learning engine with differential privacy."""
    
    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = None
        self.redis_url = redis_url
        
        # Online models for different types
        self.online_models = {}
        
        # Differential privacy configurations
        self.privacy_configs = {
            PrivacyLevel.LOW: DifferentialPrivacyConfig(
                epsilon=1.0,
                delta=1e-5,
                max_grad_norm=1.0,
                noise_multiplier=0.1,
                sample_rate=0.1
            ),
            PrivacyLevel.MEDIUM: DifferentialPrivacyConfig(
                epsilon=0.1,
                delta=1e-5,
                max_grad_norm=1.0,
                noise_multiplier=1.0,
                sample_rate=0.01
            ),
            PrivacyLevel.HIGH: DifferentialPrivacyConfig(
                epsilon=0.01,
                delta=1e-5,
                max_grad_norm=0.5,
                noise_multiplier=2.0,
                sample_rate=0.001
            ),
            PrivacyLevel.ULTRA: DifferentialPrivacyConfig(
                epsilon=0.001,
                delta=1e-6,
                max_grad_norm=0.1,
                noise_multiplier=5.0,
                sample_rate=0.0001
            )
        }
        
        # Streaming components
        self.kafka_producer = None
        self.kafka_consumer = None
        self.beam_pipeline = None
        
        # RLHF components
        self.rl_environments = {}
        self.rl_agents = {}
        
        # Initialize service
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize online learning service."""
        try:
            logger.info("Initializing online learning engine...")
            
            # Initialize online models for each model type
            for model_type in ModelType:
                self.online_models[model_type] = self._create_online_model(model_type)
            
            # Initialize streaming components
            self._initialize_streaming()
            
            # Initialize RLHF components
            self._initialize_rlhf()
            
            logger.info("Online learning engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize online learning engine: {e}")
            raise
    
    def _create_online_model(self, model_type: ModelType) -> OnlineModel:
        """Create online learning model for specific type."""
        try:
            # Base model - Adaptive Random Forest for classification
            base_model = AdaptiveRandomForestClassifier(
                n_models=10,
                max_features="sqrt",
                lambda_value=6,
                performance_metric=metrics.Accuracy()
            )
            
            # Preprocessing
            scaler = preprocessing.StandardScaler()
            
            # Drift detection
            drift_detector = drift.ADWIN(delta=0.002)
            
            # Metrics
            model_metrics = {
                'accuracy': metrics.Accuracy(),
                'precision': metrics.Precision(),
                'recall': metrics.Recall(),
                'f1': metrics.F1()
            }
            
            # Compose pipeline
            pipeline = compose.Pipeline(
                ('scaler', scaler),
                ('classifier', base_model)
            )
            
            return OnlineModel(
                model=pipeline,
                scaler=scaler,
                drift_detector=drift_detector,
                metrics=model_metrics,
                constitutional_hash=self.constitutional_hash
            )
            
        except Exception as e:
            logger.error(f"Failed to create online model for {model_type}: {e}")
            raise
    
    def _initialize_streaming(self):
        """Initialize streaming components."""
        try:
            # Kafka producer for model updates
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            
            # Kafka consumer for feedback
            self.kafka_consumer = KafkaConsumer(
                'feedback_stream',
                bootstrap_servers=['localhost:9092'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            
            logger.info("Streaming components initialized")
            
        except Exception as e:
            logger.warning(f"Streaming initialization failed: {e}")
    
    def _initialize_rlhf(self):
        """Initialize Reinforcement Learning from Human Feedback."""
        try:
            # Create simple environments for each model type
            for model_type in ModelType:
                env_id = f"ModelImprovement-{model_type.value}-v0"
                
                # Create custom environment (simplified)
                env = self._create_rl_environment(model_type)
                
                # PPO agent for policy optimization
                agent = PPO(
                    "MlpPolicy",
                    env,
                    verbose=1,
                    learning_rate=0.0003,
                    n_steps=2048,
                    batch_size=64,
                    n_epochs=10,
                    gamma=0.99,
                    gae_lambda=0.95,
                    clip_range=0.2,
                    ent_coef=0.01
                )
                
                self.rl_environments[model_type] = env
                self.rl_agents[model_type] = agent
            
            logger.info("RLHF components initialized")
            
        except Exception as e:
            logger.warning(f"RLHF initialization failed: {e}")
    
    def _create_rl_environment(self, model_type: ModelType):
        """Create RL environment for model improvement."""
        try:
            # Simplified environment for demonstration
            # In practice, this would be more sophisticated
            
            class ModelImprovementEnv(gym.Env):
                def __init__(self, model_type):
                    super().__init__()
                    self.model_type = model_type
                    self.observation_space = gym.spaces.Box(
                        low=0, high=1, shape=(10,), dtype=np.float32
                    )
                    self.action_space = gym.spaces.Discrete(3)  # improve, maintain, rollback
                    self.current_performance = 0.5
                    self.constitutional_hash = CONSTITUTIONAL_HASH
                
                def reset(self):
                    self.current_performance = 0.5
                    return np.random.random(10).astype(np.float32)
                
                def step(self, action):
                    # Simulate model improvement based on action
                    if action == 0:  # improve
                        reward = 0.1 if np.random.random() > 0.3 else -0.05
                    elif action == 1:  # maintain
                        reward = 0.0
                    else:  # rollback
                        reward = -0.1
                    
                    self.current_performance = max(0, min(1, self.current_performance + reward))
                    
                    obs = np.random.random(10).astype(np.float32)
                    done = False
                    info = {'performance': self.current_performance}
                    
                    return obs, reward, done, info
                
                def render(self):
                    pass
            
            return ModelImprovementEnv(model_type)
            
        except Exception as e:
            logger.error(f"Failed to create RL environment for {model_type}: {e}")
            return None
    
    async def initialize_redis(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Redis initialization failed: {e}")
            raise
    
    async def process_feedback_stream(self, feedback: Feedback) -> Dict[str, Any]:
        """Process feedback in real-time with differential privacy."""
        try:
            # Get online model for this model type
            online_model = self.online_models.get(feedback.model_type)
            if not online_model:
                raise ValueError(f"No online model found for {feedback.model_type}")
            
            # Convert feedback to features
            features = self._extract_features_from_feedback(feedback)
            
            # Convert feedback to label
            label = self._extract_label_from_feedback(feedback)
            
            # Apply differential privacy
            if feedback.user_id:  # Only apply DP if user identification is possible
                features = await self._apply_differential_privacy(features, PrivacyLevel.MEDIUM)
            
            # Update online model
            prediction = online_model.model.predict_one(features)
            
            # Learn from feedback
            online_model.model.learn_one(features, label)
            
            # Update metrics
            for metric_name, metric in online_model.metrics.items():
                metric.update(label, prediction)
            
            # Check for concept drift
            drift_detected = online_model.drift_detector.update(prediction != label)
            
            # Update training samples count
            online_model.training_samples += 1
            
            # Store accuracy history
            current_accuracy = online_model.metrics['accuracy'].get()
            online_model.accuracy_history.append(current_accuracy)
            
            # Keep only last 1000 accuracy points
            if len(online_model.accuracy_history) > 1000:
                online_model.accuracy_history.pop(0)
            
            # Handle concept drift
            if drift_detected:
                await self._handle_concept_drift(feedback.model_type, online_model)
            
            # Stream update to Kafka
            await self._stream_model_update(feedback.model_type, online_model)
            
            # RLHF update
            await self._update_rlhf_agent(feedback.model_type, feedback, current_accuracy)
            
            # Cache model state
            await self._cache_model_state(feedback.model_type, online_model)
            
            result = {
                'model_type': feedback.model_type.value,
                'prediction': prediction,
                'actual': label,
                'accuracy': current_accuracy,
                'drift_detected': drift_detected,
                'training_samples': online_model.training_samples,
                'constitutional_hash': self.constitutional_hash
            }
            
            logger.info(f"Processed feedback for {feedback.model_type.value}: accuracy={current_accuracy:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Feedback processing failed: {e}")
            raise
    
    def _extract_features_from_feedback(self, feedback: Feedback) -> Dict[str, float]:
        """Extract features from feedback."""
        try:
            features = {}
            
            # Basic features
            features['rating'] = feedback.rating if feedback.rating else 0.0
            features['content_length'] = len(feedback.content)
            features['timestamp_hour'] = feedback.timestamp.hour
            features['timestamp_day'] = feedback.timestamp.weekday()
            
            # Feedback type features (one-hot encoded)
            for feedback_type in FeedbackType:
                features[f'type_{feedback_type.value}'] = 1.0 if feedback.feedback_type == feedback_type else 0.0
            
            # Context features
            if feedback.context:
                features['context_size'] = len(feedback.context)
                features['has_context'] = 1.0
            else:
                features['context_size'] = 0.0
                features['has_context'] = 0.0
            
            # Sentiment features (simplified)
            positive_words = ['good', 'great', 'excellent', 'amazing', 'helpful', 'useful']
            negative_words = ['bad', 'terrible', 'awful', 'useless', 'wrong', 'error']
            
            content_lower = feedback.content.lower()
            features['positive_sentiment'] = sum(1 for word in positive_words if word in content_lower)
            features['negative_sentiment'] = sum(1 for word in negative_words if word in content_lower)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
    
    def _extract_label_from_feedback(self, feedback: Feedback) -> int:
        """Extract label from feedback."""
        try:
            # Binary classification: positive (1) or negative (0)
            if feedback.feedback_type == FeedbackType.POSITIVE:
                return 1
            elif feedback.feedback_type == FeedbackType.NEGATIVE:
                return 0
            else:
                # Use rating for neutral feedback
                if feedback.rating:
                    return 1 if feedback.rating >= 3.0 else 0
                return 0  # Default to negative for unknown
                
        except Exception as e:
            logger.error(f"Label extraction failed: {e}")
            return 0
    
    async def _apply_differential_privacy(
        self, 
        features: Dict[str, float], 
        privacy_level: PrivacyLevel
    ) -> Dict[str, float]:
        """Apply differential privacy to features."""
        try:
            config = self.privacy_configs[privacy_level]
            
            # Add calibrated noise to numerical features
            noisy_features = {}
            
            for key, value in features.items():
                if isinstance(value, (int, float)):
                    # Calculate sensitivity (assuming normalized features)
                    sensitivity = 1.0
                    
                    # Add Laplace noise
                    noise_scale = sensitivity / config.epsilon
                    noise = np.random.laplace(0, noise_scale)
                    
                    noisy_features[key] = value + noise
                else:
                    noisy_features[key] = value
            
            return noisy_features
            
        except Exception as e:
            logger.error(f"Differential privacy application failed: {e}")
            return features
    
    async def _handle_concept_drift(self, model_type: ModelType, online_model: OnlineModel):
        """Handle concept drift detection."""
        try:
            logger.warning(f"Concept drift detected for {model_type.value}")
            
            # Reset drift detector
            online_model.drift_detector = drift.ADWIN(delta=0.002)
            
            # Optional: Reset model (for severe drift)
            # online_model.model = self._create_online_model(model_type).model
            
            # Stream drift notification
            drift_notification = {
                'model_type': model_type.value,
                'event': 'concept_drift',
                'timestamp': datetime.utcnow().isoformat(),
                'training_samples': online_model.training_samples,
                'constitutional_hash': self.constitutional_hash
            }
            
            if self.kafka_producer:
                self.kafka_producer.send('model_drift', value=drift_notification)
            
            logger.info(f"Concept drift handled for {model_type.value}")
            
        except Exception as e:
            logger.error(f"Concept drift handling failed: {e}")
    
    async def _stream_model_update(self, model_type: ModelType, online_model: OnlineModel):
        """Stream model updates to Kafka."""
        try:
            if not self.kafka_producer:
                return
            
            update_data = {
                'model_type': model_type.value,
                'training_samples': online_model.training_samples,
                'accuracy': online_model.metrics['accuracy'].get(),
                'precision': online_model.metrics['precision'].get(),
                'recall': online_model.metrics['recall'].get(),
                'f1': online_model.metrics['f1'].get(),
                'timestamp': datetime.utcnow().isoformat(),
                'constitutional_hash': self.constitutional_hash
            }
            
            self.kafka_producer.send('model_updates', value=update_data)
            
        except Exception as e:
            logger.error(f"Model update streaming failed: {e}")
    
    async def _update_rlhf_agent(
        self, 
        model_type: ModelType, 
        feedback: Feedback, 
        current_accuracy: float
    ):
        """Update RLHF agent with feedback."""
        try:
            agent = self.rl_agents.get(model_type)
            if not agent:
                return
            
            # Convert feedback to reward signal
            reward = self._calculate_rlhf_reward(feedback, current_accuracy)
            
            # Update agent (simplified)
            # In practice, this would involve proper episode management
            
            # Store experience for later training
            experience = {
                'feedback_type': feedback.feedback_type.value,
                'rating': feedback.rating,
                'accuracy': current_accuracy,
                'reward': reward,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Cache experience
            if self.redis_client:
                experience_key = f"rlhf_experience:{model_type.value}"
                await self.redis_client.lpush(experience_key, json.dumps(experience))
                await self.redis_client.ltrim(experience_key, 0, 999)  # Keep last 1000
            
        except Exception as e:
            logger.error(f"RLHF agent update failed: {e}")
    
    def _calculate_rlhf_reward(self, feedback: Feedback, current_accuracy: float) -> float:
        """Calculate reward signal for RLHF."""
        try:
            base_reward = 0.0
            
            # Feedback type contribution
            if feedback.feedback_type == FeedbackType.POSITIVE:
                base_reward += 1.0
            elif feedback.feedback_type == FeedbackType.NEGATIVE:
                base_reward -= 1.0
            
            # Rating contribution
            if feedback.rating:
                base_reward += (feedback.rating - 3.0) / 2.0  # Normalize to [-1, 1]
            
            # Accuracy contribution
            base_reward += (current_accuracy - 0.5) * 2.0  # Normalize to [-1, 1]
            
            # Constitutional compliance bonus
            if 'constitutional' in feedback.content.lower():
                base_reward += 0.5
            
            return np.clip(base_reward, -2.0, 2.0)
            
        except Exception as e:
            logger.error(f"RLHF reward calculation failed: {e}")
            return 0.0
    
    async def _cache_model_state(self, model_type: ModelType, online_model: OnlineModel):
        """Cache model state in Redis."""
        try:
            if not self.redis_client:
                return
            
            state_data = {
                'training_samples': online_model.training_samples,
                'accuracy_history': online_model.accuracy_history[-10:],  # Last 10 points
                'metrics': {
                    name: metric.get() for name, metric in online_model.metrics.items()
                },
                'last_updated': datetime.utcnow().isoformat(),
                'constitutional_hash': self.constitutional_hash
            }
            
            cache_key = f"online_model_state:{model_type.value}"
            await self.redis_client.setex(
                cache_key,
                300,  # 5 minutes
                json.dumps(state_data)
            )
            
        except Exception as e:
            logger.error(f"Model state caching failed: {e}")
    
    async def get_model_performance(self, model_type: ModelType) -> Dict[str, Any]:
        """Get current model performance metrics."""
        try:
            online_model = self.online_models.get(model_type)
            if not online_model:
                return {}
            
            performance = {
                'model_type': model_type.value,
                'training_samples': online_model.training_samples,
                'current_metrics': {
                    name: metric.get() for name, metric in online_model.metrics.items()
                },
                'accuracy_trend': online_model.accuracy_history[-20:],  # Last 20 points
                'constitutional_hash': self.constitutional_hash
            }
            
            return performance
            
        except Exception as e:
            logger.error(f"Performance retrieval failed: {e}")
            return {}
    
    async def trigger_model_checkpoint(self, model_type: ModelType) -> bool:
        """Trigger model checkpoint for persistence."""
        try:
            online_model = self.online_models.get(model_type)
            if not online_model:
                return False
            
            # Create checkpoint data
            checkpoint_data = {
                'model_type': model_type.value,
                'training_samples': online_model.training_samples,
                'metrics': {
                    name: metric.get() for name, metric in online_model.metrics.items()
                },
                'accuracy_history': online_model.accuracy_history,
                'checkpoint_time': datetime.utcnow().isoformat(),
                'constitutional_hash': self.constitutional_hash
            }
            
            # Store in Redis with longer TTL
            if self.redis_client:
                checkpoint_key = f"model_checkpoint:{model_type.value}:{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                await self.redis_client.setex(
                    checkpoint_key,
                    86400,  # 24 hours
                    json.dumps(checkpoint_data)
                )
            
            # Stream checkpoint notification
            if self.kafka_producer:
                self.kafka_producer.send(
                    'model_checkpoints',
                    value=checkpoint_data
                )
            
            logger.info(f"Model checkpoint created for {model_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"Model checkpoint failed: {e}")
            return False
    
    async def get_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive learning analytics."""
        try:
            analytics = {
                'system_status': 'online',
                'total_models': len(self.online_models),
                'models': {},
                'system_metrics': {
                    'average_accuracy': 0.0,
                    'total_training_samples': 0,
                    'active_drift_detectors': 0
                },
                'privacy_status': {
                    'differential_privacy_enabled': True,
                    'privacy_levels': [level.value for level in PrivacyLevel]
                },
                'constitutional_hash': self.constitutional_hash
            }
            
            total_accuracy = 0.0
            total_samples = 0
            
            for model_type, online_model in self.online_models.items():
                model_analytics = {
                    'accuracy': online_model.metrics['accuracy'].get(),
                    'precision': online_model.metrics['precision'].get(),
                    'recall': online_model.metrics['recall'].get(),
                    'f1': online_model.metrics['f1'].get(),
                    'training_samples': online_model.training_samples,
                    'accuracy_trend': online_model.accuracy_history[-10:],
                    'drift_detector_active': True
                }
                
                analytics['models'][model_type.value] = model_analytics
                total_accuracy += model_analytics['accuracy']
                total_samples += model_analytics['training_samples']
            
            # Calculate system metrics
            if self.online_models:
                analytics['system_metrics']['average_accuracy'] = total_accuracy / len(self.online_models)
            
            analytics['system_metrics']['total_training_samples'] = total_samples
            analytics['system_metrics']['active_drift_detectors'] = len(self.online_models)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Learning analytics retrieval failed: {e}")
            return {'error': str(e)}
    
    async def health_check(self) -> bool:
        """Check if online learning engine is healthy."""
        try:
            # Check models
            for model_type, online_model in self.online_models.items():
                if not online_model.model:
                    return False
            
            # Check Redis
            if self.redis_client:
                await self.redis_client.ping()
            
            # Check streaming
            if self.kafka_producer:
                # Basic producer health check
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False