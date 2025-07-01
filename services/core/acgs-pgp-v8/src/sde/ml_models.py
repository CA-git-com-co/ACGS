"""
Machine Learning Models for Syndrome Diagnosis

Implements trained ML models for error classification, anomaly detection,
and recovery recommendation in the ACGS-PGP v8 system.
"""

import logging
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# ML dependencies
try:
    from sklearn.ensemble import (
        RandomForestClassifier,
        IsolationForest,
        GradientBoostingClassifier,
    )
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.pipeline import Pipeline
    from sklearn.decomposition import PCA
    from sklearn.cluster import DBSCAN
    import joblib

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Deep learning dependencies (optional)
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

from .models import ErrorCategory, ErrorSeverity, RecoveryStrategy

logger = logging.getLogger(__name__)


@dataclass
class TrainingData:
    """Training data container for ML models."""

    features: np.ndarray
    labels: np.ndarray
    feature_names: List[str]
    label_names: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate training data after initialization."""
        if len(self.features) != len(self.labels):
            raise ValueError("Features and labels must have same length")

        if len(self.features) == 0:
            raise ValueError("Training data cannot be empty")


@dataclass
class ModelMetrics:
    """Model performance metrics."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: np.ndarray
    classification_report: str
    cross_val_scores: List[float]
    training_time: float
    model_size_mb: float


class ErrorClassificationModel:
    """ML model for error classification and severity prediction."""

    def __init__(self, model_type: str = "random_forest"):
        """
        Initialize error classification model.

        Args:
            model_type: Type of ML model ('random_forest', 'gradient_boosting', 'neural_network')
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_trained = False
        self.training_metrics = None

        # Initialize model based on type
        if model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=100, max_depth=10, random_state=42, class_weight="balanced"
            )
        elif model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(
                n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42
            )
        elif model_type == "neural_network" and TORCH_AVAILABLE:
            self.model = ErrorClassificationNN()
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        logger.info(f"Initialized {model_type} error classification model")

    def extract_features(self, error_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from error data for ML processing.

        Args:
            error_data: Dictionary containing error information

        Returns:
            Feature vector as numpy array
        """
        features = []

        # Temporal features
        timestamp = error_data.get("timestamp", datetime.now())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        features.extend(
            [
                timestamp.hour,  # Hour of day
                timestamp.weekday(),  # Day of week
                timestamp.month,  # Month
            ]
        )

        # System state features
        features.extend(
            [
                error_data.get("cpu_usage", 0.0),
                error_data.get("memory_usage", 0.0),
                error_data.get("disk_usage", 0.0),
                error_data.get("network_latency", 0.0),
                error_data.get("active_connections", 0),
                error_data.get("queue_length", 0),
            ]
        )

        # Error context features
        features.extend(
            [
                len(error_data.get("error_message", "")),
                error_data.get("error_code", 0),
                error_data.get("retry_count", 0),
                error_data.get("response_time_ms", 0.0),
                int(error_data.get("constitutional_compliance_score", 0.8) * 100),
            ]
        )

        # Quantum state features (if available)
        quantum_state = error_data.get("quantum_state", {})
        features.extend(
            [
                quantum_state.get("entanglement_strength", 0.0),
                quantum_state.get("coherence_time", 1.0),
                len(quantum_state.get("error_syndrome", [])),
                len(quantum_state.get("correction_history", [])),
            ]
        )

        # Stabilizer features
        stabilizer_results = error_data.get("stabilizer_results", [])
        features.extend(
            [
                len(stabilizer_results),
                sum(1 for r in stabilizer_results if r.get("status") == "success"),
                sum(1 for r in stabilizer_results if r.get("status") == "failure"),
                (
                    np.mean([r.get("execution_time", 0.0) for r in stabilizer_results])
                    if stabilizer_results
                    else 0.0
                ),
            ]
        )

        return np.array(features, dtype=np.float32)

    def train(self, training_data: TrainingData) -> ModelMetrics:
        """
        Train the error classification model.

        Args:
            training_data: Training data container

        Returns:
            Model performance metrics
        """
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("Scikit-learn not available for training")

        start_time = datetime.now()

        # Prepare data
        X = training_data.features
        y = training_data.labels

        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        # Train model
        if self.model_type == "neural_network" and TORCH_AVAILABLE:
            metrics = self._train_neural_network(
                X_train_scaled, y_train, X_test_scaled, y_test
            )
        else:
            self.model.fit(X_train_scaled, y_train)

            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            metrics = self._calculate_metrics(y_test, y_pred, X_train_scaled, y_train)

        # Calculate training time
        training_time = (datetime.now() - start_time).total_seconds()
        metrics.training_time = training_time

        # Store feature names
        self.feature_names = training_data.feature_names
        self.is_trained = True
        self.training_metrics = metrics

        logger.info(
            f"Model training completed in {training_time:.2f}s with accuracy {metrics.accuracy:.3f}"
        )
        return metrics

    def _train_neural_network(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
    ) -> ModelMetrics:
        """Train neural network model."""
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch not available for neural network training")

        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train)
        y_train_tensor = torch.LongTensor(y_train)
        X_test_tensor = torch.FloatTensor(X_test)
        y_test_tensor = torch.LongTensor(y_test)

        # Create data loaders
        train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

        # Initialize model
        input_size = X_train.shape[1]
        num_classes = len(np.unique(y_train))
        self.model = ErrorClassificationNN(input_size, num_classes)

        # Training setup
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        # Training loop
        self.model.train()
        for epoch in range(50):
            for batch_X, batch_y in train_loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

        # Evaluation
        self.model.eval()
        with torch.no_grad():
            test_outputs = self.model(X_test_tensor)
            _, y_pred = torch.max(test_outputs, 1)
            y_pred = y_pred.numpy()

        return self._calculate_metrics(y_test, y_pred, X_train, y_train)

    def _calculate_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        X_train: np.ndarray,
        y_train: np.ndarray,
    ) -> ModelMetrics:
        """Calculate model performance metrics."""
        from sklearn.metrics import (
            accuracy_score,
            precision_score,
            recall_score,
            f1_score,
        )

        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average="weighted")
        recall = recall_score(y_true, y_pred, average="weighted")
        f1 = f1_score(y_true, y_pred, average="weighted")

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)

        # Classification report
        report = classification_report(y_true, y_pred)

        # Cross-validation scores
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)

        # Model size estimation
        model_size_mb = 0.1  # Placeholder

        return ModelMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            confusion_matrix=cm,
            classification_report=report,
            cross_val_scores=cv_scores.tolist(),
            training_time=0.0,  # Will be set by caller
            model_size_mb=model_size_mb,
        )

    def predict(self, error_data: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
        """
        Predict error classification and severity.

        Args:
            error_data: Error data dictionary

        Returns:
            Tuple of (predicted_class, confidence, additional_info)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before prediction")

        # Extract features
        features = self.extract_features(error_data)
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Make prediction
        if self.model_type == "neural_network" and TORCH_AVAILABLE:
            self.model.eval()
            with torch.no_grad():
                features_tensor = torch.FloatTensor(features_scaled)
                outputs = self.model(features_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted_idx = torch.max(probabilities, 1)
                predicted_class = self.label_encoder.inverse_transform(
                    [predicted_idx.item()]
                )[0]
                confidence = confidence.item()
        else:
            predicted_idx = self.model.predict(features_scaled)[0]
            predicted_class = self.label_encoder.inverse_transform([predicted_idx])[0]

            # Get prediction probabilities for confidence
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(features_scaled)[0]
                confidence = np.max(probabilities)
            else:
                confidence = 0.8  # Default confidence

        # Additional information
        additional_info = {
            "feature_importance": self._get_feature_importance(),
            "prediction_timestamp": datetime.now().isoformat(),
            "model_type": self.model_type,
            "training_accuracy": (
                self.training_metrics.accuracy if self.training_metrics else None
            ),
        }

        return predicted_class, confidence, additional_info

    def _get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores."""
        if hasattr(self.model, "feature_importances_"):
            importance_scores = self.model.feature_importances_
            return dict(zip(self.feature_names, importance_scores))
        return {}

    def save_model(self, file_path: Path):
        """Save trained model to file."""
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")

        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "label_encoder": self.label_encoder,
            "feature_names": self.feature_names,
            "model_type": self.model_type,
            "training_metrics": self.training_metrics,
            "is_trained": self.is_trained,
        }

        joblib.dump(model_data, file_path)
        logger.info(f"Model saved to {file_path}")

    def load_model(self, file_path: Path):
        """Load trained model from file."""
        model_data = joblib.load(file_path)

        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.label_encoder = model_data["label_encoder"]
        self.feature_names = model_data["feature_names"]
        self.model_type = model_data["model_type"]
        self.training_metrics = model_data["training_metrics"]
        self.is_trained = model_data["is_trained"]

        logger.info(f"Model loaded from {file_path}")


class ErrorClassificationNN(nn.Module):
    """Neural network for error classification."""

    def __init__(self, input_size: int = 20, num_classes: int = 5):
        super(ErrorClassificationNN, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 16)
        self.fc4 = nn.Linear(16, num_classes)
        self.dropout = nn.Dropout(0.2)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.fc4(x)
        return x


class AnomalyDetectionModel:
    """ML model for anomaly detection in system behavior."""

    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detection model.

        Args:
            contamination: Expected proportion of anomalies in data
        """
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination, random_state=42, n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False

        logger.info(
            f"Initialized anomaly detection model with contamination {contamination}"
        )

    def train(self, normal_data: np.ndarray) -> Dict[str, Any]:
        """
        Train anomaly detection model on normal system behavior.

        Args:
            normal_data: Normal system behavior data

        Returns:
            Training metrics
        """
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("Scikit-learn not available for training")

        # Scale data
        normal_data_scaled = self.scaler.fit_transform(normal_data)

        # Train model
        self.model.fit(normal_data_scaled)
        self.is_trained = True

        # Calculate training metrics
        anomaly_scores = self.model.decision_function(normal_data_scaled)

        metrics = {
            "training_samples": len(normal_data),
            "mean_anomaly_score": np.mean(anomaly_scores),
            "std_anomaly_score": np.std(anomaly_scores),
            "contamination": self.contamination,
        }

        logger.info(f"Anomaly detection model trained on {len(normal_data)} samples")
        return metrics

    def detect_anomaly(self, data: np.ndarray) -> Tuple[bool, float]:
        """
        Detect if data point is anomalous.

        Args:
            data: Data point to check

        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before anomaly detection")

        # Scale data
        data_scaled = self.scaler.transform(data.reshape(1, -1))

        # Predict anomaly
        is_anomaly = self.model.predict(data_scaled)[0] == -1
        anomaly_score = self.model.decision_function(data_scaled)[0]

        return is_anomaly, anomaly_score


class RecoveryRecommendationModel:
    """ML model for generating recovery recommendations."""

    def __init__(self):
        """Initialize recovery recommendation model."""
        self.text_vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
        self.classifier = RandomForestClassifier(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False

        logger.info("Initialized recovery recommendation model")

    def train(
        self, error_descriptions: List[str], recovery_strategies: List[str]
    ) -> Dict[str, Any]:
        """
        Train recovery recommendation model.

        Args:
            error_descriptions: List of error descriptions
            recovery_strategies: List of corresponding recovery strategies

        Returns:
            Training metrics
        """
        if not SKLEARN_AVAILABLE:
            raise RuntimeError("Scikit-learn not available for training")

        # Vectorize text
        text_features = self.text_vectorizer.fit_transform(error_descriptions)

        # Train classifier
        self.classifier.fit(text_features, recovery_strategies)
        self.is_trained = True

        # Calculate accuracy
        predictions = self.classifier.predict(text_features)
        accuracy = np.mean(predictions == recovery_strategies)

        metrics = {
            "training_samples": len(error_descriptions),
            "accuracy": accuracy,
            "unique_strategies": len(set(recovery_strategies)),
            "vocabulary_size": len(self.text_vectorizer.vocabulary_),
        }

        logger.info(
            f"Recovery recommendation model trained with {accuracy:.3f} accuracy"
        )
        return metrics

    def recommend_recovery(self, error_description: str) -> Tuple[str, float]:
        """
        Recommend recovery strategy for error.

        Args:
            error_description: Description of the error

        Returns:
            Tuple of (recommended_strategy, confidence)
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before making recommendations")

        # Vectorize error description
        text_features = self.text_vectorizer.transform([error_description])

        # Predict recovery strategy
        strategy = self.classifier.predict(text_features)[0]

        # Get confidence
        if hasattr(self.classifier, "predict_proba"):
            probabilities = self.classifier.predict_proba(text_features)[0]
            confidence = np.max(probabilities)
        else:
            confidence = 0.7  # Default confidence

        return strategy, confidence


class TrainingDataGenerator:
    """Generate synthetic training data for ML models."""

    def __init__(self, seed: int = 42):
        """Initialize training data generator."""
        np.random.seed(seed)
        self.seed = seed

        # Define error categories and their characteristics
        self.error_patterns = {
            "SYSTEM_OVERLOAD": {
                "cpu_range": (0.8, 1.0),
                "memory_range": (0.7, 1.0),
                "response_time_range": (1000, 5000),
                "error_codes": [503, 504, 429],
                "recovery_strategies": ["SCALE_UP", "LOAD_BALANCE", "CIRCUIT_BREAKER"],
            },
            "NETWORK_FAILURE": {
                "cpu_range": (0.1, 0.5),
                "memory_range": (0.2, 0.6),
                "network_latency_range": (500, 2000),
                "error_codes": [502, 504, 408],
                "recovery_strategies": ["RETRY", "FAILOVER", "CIRCUIT_BREAKER"],
            },
            "CONSTITUTIONAL_VIOLATION": {
                "compliance_score_range": (0.0, 0.7),
                "error_codes": [400, 403, 422],
                "recovery_strategies": [
                    "POLICY_REVIEW",
                    "COMPLIANCE_CHECK",
                    "MANUAL_REVIEW",
                ],
            },
            "QUANTUM_DECOHERENCE": {
                "entanglement_range": (0.0, 0.3),
                "coherence_time_range": (0.1, 0.5),
                "error_codes": [500, 422],
                "recovery_strategies": [
                    "QUANTUM_CORRECTION",
                    "STATE_RESET",
                    "FALLBACK_CLASSICAL",
                ],
            },
            "DATA_CORRUPTION": {
                "error_syndrome_length_range": (1, 5),
                "error_codes": [500, 422, 400],
                "recovery_strategies": [
                    "ERROR_CORRECTION",
                    "BACKUP_RESTORE",
                    "DATA_VALIDATION",
                ],
            },
        }

        logger.info("Training data generator initialized")

    def generate_error_classification_data(self, n_samples: int = 1000) -> TrainingData:
        """Generate training data for error classification."""
        features = []
        labels = []

        for _ in range(n_samples):
            # Randomly select error category
            error_category = np.random.choice(list(self.error_patterns.keys()))
            pattern = self.error_patterns[error_category]

            # Generate features based on error pattern
            sample_features = self._generate_sample_features(pattern)

            features.append(sample_features)
            labels.append(error_category)

        feature_names = [
            "hour",
            "weekday",
            "month",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "network_latency",
            "active_connections",
            "queue_length",
            "error_message_length",
            "error_code",
            "retry_count",
            "response_time_ms",
            "constitutional_compliance_score",
            "entanglement_strength",
            "coherence_time",
            "error_syndrome_length",
            "correction_history_length",
            "stabilizer_count",
            "stabilizer_success",
            "stabilizer_failure",
            "avg_stabilizer_time",
        ]

        return TrainingData(
            features=np.array(features),
            labels=np.array(labels),
            feature_names=feature_names,
            label_names=list(self.error_patterns.keys()),
            metadata={"generation_seed": self.seed, "n_samples": n_samples},
        )

    def _generate_sample_features(self, pattern: Dict[str, Any]) -> List[float]:
        """Generate sample features based on error pattern."""
        features = []

        # Temporal features
        features.extend(
            [
                np.random.randint(0, 24),  # hour
                np.random.randint(0, 7),  # weekday
                np.random.randint(1, 13),  # month
            ]
        )

        # System state features
        cpu_range = pattern.get("cpu_range", (0.1, 0.8))
        memory_range = pattern.get("memory_range", (0.2, 0.7))

        features.extend(
            [
                np.random.uniform(*cpu_range),
                np.random.uniform(*memory_range),
                np.random.uniform(0.1, 0.9),  # disk_usage
                np.random.uniform(*pattern.get("network_latency_range", (10, 100))),
                np.random.randint(1, 100),  # active_connections
                np.random.randint(0, 50),  # queue_length
            ]
        )

        # Error context features
        features.extend(
            [
                np.random.randint(10, 200),  # error_message_length
                np.random.choice(pattern.get("error_codes", [500])),
                np.random.randint(0, 5),  # retry_count
                np.random.uniform(*pattern.get("response_time_range", (100, 1000))),
                np.random.uniform(*pattern.get("compliance_score_range", (0.8, 1.0)))
                * 100,
            ]
        )

        # Quantum state features
        features.extend(
            [
                np.random.uniform(*pattern.get("entanglement_range", (0.3, 0.8))),
                np.random.uniform(*pattern.get("coherence_time_range", (0.5, 2.0))),
                np.random.randint(*pattern.get("error_syndrome_length_range", (0, 3))),
                np.random.randint(0, 10),  # correction_history_length
            ]
        )

        # Stabilizer features
        stabilizer_count = np.random.randint(1, 10)
        stabilizer_success = np.random.randint(0, stabilizer_count + 1)

        features.extend(
            [
                stabilizer_count,
                stabilizer_success,
                stabilizer_count - stabilizer_success,  # failures
                np.random.uniform(10, 500),  # avg_stabilizer_time
            ]
        )

        return features

    def generate_recovery_recommendation_data(
        self, n_samples: int = 500
    ) -> Tuple[List[str], List[str]]:
        """Generate training data for recovery recommendations."""
        error_descriptions = []
        recovery_strategies = []

        error_templates = {
            "SYSTEM_OVERLOAD": [
                "High CPU usage detected at {cpu}%",
                "Memory usage exceeded threshold at {memory}%",
                "Response time degraded to {response_time}ms",
                "Queue length increased to {queue_length} items",
            ],
            "NETWORK_FAILURE": [
                "Network latency increased to {latency}ms",
                "Connection timeout after {timeout}s",
                "Service unavailable error {error_code}",
                "Failed to connect to external service",
            ],
            "CONSTITUTIONAL_VIOLATION": [
                "Constitutional compliance score dropped to {score}",
                "Policy validation failed with error {error_code}",
                "Governance rule violation detected",
                "Constitutional hash mismatch",
            ],
            "QUANTUM_DECOHERENCE": [
                "Quantum entanglement strength reduced to {entanglement}",
                "Coherence time decreased to {coherence_time}s",
                "Error syndrome detected: {syndrome}",
                "Quantum state corruption identified",
            ],
            "DATA_CORRUPTION": [
                "Data integrity check failed",
                "Checksum mismatch detected",
                "Database corruption error {error_code}",
                "Semantic hash validation failed",
            ],
        }

        for _ in range(n_samples):
            # Select random error category
            category = np.random.choice(list(error_templates.keys()))
            template = np.random.choice(error_templates[category])
            strategy = np.random.choice(
                self.error_patterns[category]["recovery_strategies"]
            )

            # Fill template with random values
            description = template.format(
                cpu=np.random.randint(80, 100),
                memory=np.random.randint(70, 100),
                response_time=np.random.randint(1000, 5000),
                queue_length=np.random.randint(50, 200),
                latency=np.random.randint(500, 2000),
                timeout=np.random.randint(5, 30),
                error_code=np.random.choice([400, 403, 422, 500, 502, 503, 504]),
                score=np.random.uniform(0.1, 0.7),
                entanglement=np.random.uniform(0.0, 0.3),
                coherence_time=np.random.uniform(0.1, 0.5),
                syndrome=np.random.randint(1, 8),
            )

            error_descriptions.append(description)
            recovery_strategies.append(strategy)

        return error_descriptions, recovery_strategies


class MLModelTrainer:
    """Trainer for all ML models in the syndrome diagnosis system."""

    def __init__(self, models_dir: Path = Path("models")):
        """Initialize ML model trainer."""
        self.models_dir = models_dir
        self.models_dir.mkdir(exist_ok=True)

        self.data_generator = TrainingDataGenerator()
        self.trained_models = {}

        logger.info(f"ML model trainer initialized with models directory: {models_dir}")

    def train_all_models(self) -> Dict[str, Any]:
        """Train all ML models and save them."""
        results = {}

        # Train error classification model
        logger.info("Training error classification model...")
        classification_results = self._train_error_classification_model()
        results["error_classification"] = classification_results

        # Train anomaly detection model
        logger.info("Training anomaly detection model...")
        anomaly_results = self._train_anomaly_detection_model()
        results["anomaly_detection"] = anomaly_results

        # Train recovery recommendation model
        logger.info("Training recovery recommendation model...")
        recovery_results = self._train_recovery_recommendation_model()
        results["recovery_recommendation"] = recovery_results

        logger.info("All ML models trained successfully")
        return results

    def _train_error_classification_model(self) -> Dict[str, Any]:
        """Train error classification model."""
        # Generate training data
        training_data = self.data_generator.generate_error_classification_data(
            n_samples=2000
        )

        # Train different model types
        model_results = {}

        for model_type in ["random_forest", "gradient_boosting"]:
            try:
                model = ErrorClassificationModel(model_type=model_type)
                metrics = model.train(training_data)

                # Save model
                model_path = (
                    self.models_dir / f"error_classification_{model_type}.joblib"
                )
                model.save_model(model_path)

                model_results[model_type] = {
                    "metrics": metrics,
                    "model_path": str(model_path),
                }

                self.trained_models[f"error_classification_{model_type}"] = model

            except Exception as e:
                logger.error(f"Failed to train {model_type} model: {e}")
                model_results[model_type] = {"error": str(e)}

        return model_results

    def _train_anomaly_detection_model(self) -> Dict[str, Any]:
        """Train anomaly detection model."""
        # Generate normal system behavior data
        normal_data = []
        for _ in range(1000):
            features = [
                np.random.uniform(0.1, 0.7),  # cpu_usage
                np.random.uniform(0.2, 0.6),  # memory_usage
                np.random.uniform(0.1, 0.5),  # disk_usage
                np.random.uniform(10, 100),  # network_latency
                np.random.randint(1, 50),  # active_connections
                np.random.uniform(100, 500),  # response_time
                np.random.uniform(0.8, 1.0),  # compliance_score
            ]
            normal_data.append(features)

        normal_data = np.array(normal_data)

        try:
            model = AnomalyDetectionModel(contamination=0.1)
            metrics = model.train(normal_data)

            # Save model
            model_path = self.models_dir / "anomaly_detection.joblib"
            joblib.dump(model, model_path)

            self.trained_models["anomaly_detection"] = model

            return {"metrics": metrics, "model_path": str(model_path)}

        except Exception as e:
            logger.error(f"Failed to train anomaly detection model: {e}")
            return {"error": str(e)}

    def _train_recovery_recommendation_model(self) -> Dict[str, Any]:
        """Train recovery recommendation model."""
        try:
            # Generate training data
            error_descriptions, recovery_strategies = (
                self.data_generator.generate_recovery_recommendation_data(
                    n_samples=1000
                )
            )

            model = RecoveryRecommendationModel()
            metrics = model.train(error_descriptions, recovery_strategies)

            # Save model
            model_path = self.models_dir / "recovery_recommendation.joblib"
            joblib.dump(model, model_path)

            self.trained_models["recovery_recommendation"] = model

            return {"metrics": metrics, "model_path": str(model_path)}

        except Exception as e:
            logger.error(f"Failed to train recovery recommendation model: {e}")
            return {"error": str(e)}
