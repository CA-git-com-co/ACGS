"""
Tests for ML-powered Syndrome Diagnosis

Comprehensive tests for machine learning models used in error classification,
anomaly detection, and recovery recommendation systems.
"""

import pytest
import numpy as np
from datetime import datetime
from unittest.mock import patch, MagicMock
from pathlib import Path

from services.core.acgs_pgp_v8.src.sde.ml_models import (
    ErrorClassificationModel,
    AnomalyDetectionModel,
    RecoveryRecommendationModel,
    TrainingDataGenerator,
    MLModelTrainer,
    TrainingData,
    ModelMetrics,
)


class TestTrainingDataGenerator:
    """Test training data generation for ML models."""

    @pytest.fixture
    def data_generator(self):
        """Create training data generator for testing."""
        return TrainingDataGenerator(seed=42)

    def test_error_classification_data_generation(self, data_generator):
        """Test error classification training data generation."""
        training_data = data_generator.generate_error_classification_data(n_samples=100)

        assert isinstance(training_data, TrainingData)
        assert len(training_data.features) == 100
        assert len(training_data.labels) == 100
        assert len(training_data.feature_names) > 0
        assert len(training_data.label_names) > 0

        # Check feature dimensions
        assert training_data.features.shape[1] == len(training_data.feature_names)

        # Check label categories
        unique_labels = set(training_data.labels)
        assert len(unique_labels) > 1
        assert all(label in data_generator.error_patterns for label in unique_labels)

    def test_recovery_recommendation_data_generation(self, data_generator):
        """Test recovery recommendation training data generation."""
        error_descriptions, recovery_strategies = (
            data_generator.generate_recovery_recommendation_data(n_samples=50)
        )

        assert len(error_descriptions) == 50
        assert len(recovery_strategies) == 50
        assert all(isinstance(desc, str) for desc in error_descriptions)
        assert all(isinstance(strategy, str) for strategy in recovery_strategies)

        # Check that descriptions contain meaningful content
        assert all(len(desc) > 10 for desc in error_descriptions)

    def test_sample_feature_generation(self, data_generator):
        """Test individual sample feature generation."""
        pattern = {
            "cpu_range": (0.8, 1.0),
            "memory_range": (0.7, 1.0),
            "error_codes": [503, 504],
            "response_time_range": (1000, 5000),
        }

        features = data_generator._generate_sample_features(pattern)

        assert len(features) > 0
        assert all(isinstance(f, (int, float)) for f in features)

        # Check that CPU and memory are in expected ranges
        cpu_usage = features[3]  # CPU usage is 4th feature
        memory_usage = features[4]  # Memory usage is 5th feature

        assert 0.8 <= cpu_usage <= 1.0
        assert 0.7 <= memory_usage <= 1.0


class TestErrorClassificationModel:
    """Test error classification ML model."""

    @pytest.fixture
    def sample_training_data(self):
        """Create sample training data for testing."""
        generator = TrainingDataGenerator(seed=42)
        return generator.generate_error_classification_data(n_samples=100)

    def test_model_initialization(self):
        """Test error classification model initialization."""
        model = ErrorClassificationModel("random_forest")

        assert model.model_type == "random_forest"
        assert model.model is not None
        assert not model.is_trained
        assert model.training_metrics is None

    def test_feature_extraction(self):
        """Test feature extraction from error data."""
        model = ErrorClassificationModel("random_forest")

        error_data = {
            "timestamp": datetime.now(),
            "cpu_usage": 0.8,
            "memory_usage": 0.7,
            "network_latency": 100.0,
            "error_code": 503,
            "constitutional_compliance_score": 0.85,
            "quantum_state": {
                "entanglement_strength": 0.5,
                "coherence_time": 1.0,
                "error_syndrome": [1, 0, 1],
                "correction_history": ["X0", "Z1"],
            },
            "stabilizer_results": [
                {"status": "success", "execution_time": 100.0},
                {"status": "failure", "execution_time": 200.0},
            ],
        }

        features = model.extract_features(error_data)

        assert isinstance(features, np.ndarray)
        assert len(features) > 0
        assert features.dtype == np.float32

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_model_training(self, sample_training_data):
        """Test model training process."""
        model = ErrorClassificationModel("random_forest")

        # Mock sklearn components
        with patch.object(model, "model") as mock_model:
            with patch.object(model, "scaler") as mock_scaler:
                with patch.object(model, "label_encoder") as mock_encoder:
                    # Setup mocks
                    mock_encoder.fit_transform.return_value = np.array(
                        [0, 1, 2, 0, 1] * 20
                    )
                    mock_encoder.inverse_transform.return_value = ["SYSTEM_OVERLOAD"]
                    mock_scaler.fit_transform.return_value = (
                        sample_training_data.features[:80]
                    )
                    mock_scaler.transform.return_value = sample_training_data.features[
                        80:
                    ]
                    mock_model.fit.return_value = None
                    mock_model.predict.return_value = np.array([0] * 20)
                    mock_model.feature_importances_ = np.random.random(
                        len(sample_training_data.feature_names)
                    )

                    # Train model
                    metrics = model.train(sample_training_data)

                    assert isinstance(metrics, ModelMetrics)
                    assert 0.0 <= metrics.accuracy <= 1.0
                    assert model.is_trained
                    assert model.training_metrics is not None

    def test_prediction_without_training(self):
        """Test that prediction fails without training."""
        model = ErrorClassificationModel("random_forest")

        error_data = {"timestamp": datetime.now(), "cpu_usage": 0.8}

        with pytest.raises(RuntimeError, match="Model must be trained"):
            model.predict(error_data)

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", False)
    def test_model_initialization_without_sklearn(self):
        """Test model initialization when sklearn is not available."""
        with pytest.raises(ValueError):
            ErrorClassificationModel("random_forest")


class TestAnomalyDetectionModel:
    """Test anomaly detection ML model."""

    @pytest.fixture
    def normal_data(self):
        """Create normal system behavior data for testing."""
        np.random.seed(42)
        return np.random.uniform(0.1, 0.7, (100, 7))

    def test_model_initialization(self):
        """Test anomaly detection model initialization."""
        model = AnomalyDetectionModel(contamination=0.1)

        assert model.contamination == 0.1
        assert not model.is_trained

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_model_training(self, normal_data):
        """Test anomaly detection model training."""
        model = AnomalyDetectionModel(contamination=0.1)

        # Mock sklearn components
        with patch.object(model, "model") as mock_model:
            with patch.object(model, "scaler") as mock_scaler:
                mock_scaler.fit_transform.return_value = normal_data
                mock_model.fit.return_value = None
                mock_model.decision_function.return_value = np.random.uniform(
                    -1, 1, len(normal_data)
                )

                metrics = model.train(normal_data)

                assert isinstance(metrics, dict)
                assert "training_samples" in metrics
                assert "mean_anomaly_score" in metrics
                assert metrics["training_samples"] == len(normal_data)
                assert model.is_trained

    def test_anomaly_detection_without_training(self):
        """Test that anomaly detection fails without training."""
        model = AnomalyDetectionModel()

        test_data = np.array([[0.5, 0.4, 0.3, 50, 25, 300, 0.9]])

        with pytest.raises(RuntimeError, match="Model must be trained"):
            model.detect_anomaly(test_data)

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_anomaly_detection(self, normal_data):
        """Test anomaly detection functionality."""
        model = AnomalyDetectionModel(contamination=0.1)

        # Mock training
        with patch.object(model, "model") as mock_model:
            with patch.object(model, "scaler") as mock_scaler:
                mock_scaler.fit_transform.return_value = normal_data
                mock_scaler.transform.return_value = np.array(
                    [[0.5, 0.4, 0.3, 50, 25, 300, 0.9]]
                )
                mock_model.fit.return_value = None
                mock_model.decision_function.return_value = np.array([0.5])
                mock_model.predict.return_value = np.array([1])  # Normal

                # Train model
                model.train(normal_data)
                model.is_trained = True

                # Test detection
                test_data = np.array([[0.5, 0.4, 0.3, 50, 25, 300, 0.9]])
                is_anomaly, score = model.detect_anomaly(test_data)

                assert isinstance(is_anomaly, bool)
                assert isinstance(score, (int, float))


class TestRecoveryRecommendationModel:
    """Test recovery recommendation ML model."""

    @pytest.fixture
    def sample_data(self):
        """Create sample recovery recommendation data."""
        error_descriptions = [
            "High CPU usage detected at 95%",
            "Network latency increased to 2000ms",
            "Constitutional compliance score dropped to 0.6",
            "Quantum entanglement strength reduced to 0.2",
        ]
        recovery_strategies = [
            "SCALE_UP",
            "RETRY",
            "POLICY_REVIEW",
            "QUANTUM_CORRECTION",
        ]
        return error_descriptions, recovery_strategies

    def test_model_initialization(self):
        """Test recovery recommendation model initialization."""
        model = RecoveryRecommendationModel()

        assert not model.is_trained
        assert model.text_vectorizer is not None
        assert model.classifier is not None

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_model_training(self, sample_data):
        """Test recovery recommendation model training."""
        error_descriptions, recovery_strategies = sample_data
        model = RecoveryRecommendationModel()

        # Mock sklearn components
        with patch.object(model, "text_vectorizer") as mock_vectorizer:
            with patch.object(model, "classifier") as mock_classifier:
                mock_vectorizer.fit_transform.return_value = np.random.random((4, 100))
                mock_classifier.fit.return_value = None
                mock_classifier.predict.return_value = recovery_strategies

                metrics = model.train(error_descriptions, recovery_strategies)

                assert isinstance(metrics, dict)
                assert "training_samples" in metrics
                assert "accuracy" in metrics
                assert metrics["training_samples"] == len(error_descriptions)
                assert model.is_trained

    def test_recommendation_without_training(self):
        """Test that recommendation fails without training."""
        model = RecoveryRecommendationModel()

        with pytest.raises(RuntimeError, match="Model must be trained"):
            model.recommend_recovery("Test error")

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_recovery_recommendation(self, sample_data):
        """Test recovery recommendation functionality."""
        error_descriptions, recovery_strategies = sample_data
        model = RecoveryRecommendationModel()

        # Mock training and prediction
        with patch.object(model, "text_vectorizer") as mock_vectorizer:
            with patch.object(model, "classifier") as mock_classifier:
                mock_vectorizer.fit_transform.return_value = np.random.random((4, 100))
                mock_vectorizer.transform.return_value = np.random.random((1, 100))
                mock_classifier.fit.return_value = None
                mock_classifier.predict.return_value = ["SCALE_UP"]
                mock_classifier.predict_proba.return_value = np.array([[0.1, 0.8, 0.1]])

                # Train model
                model.train(error_descriptions, recovery_strategies)
                model.is_trained = True

                # Test recommendation
                strategy, confidence = model.recommend_recovery(
                    "High CPU usage detected"
                )

                assert isinstance(strategy, str)
                assert isinstance(confidence, (int, float))
                assert 0.0 <= confidence <= 1.0


class TestMLModelTrainer:
    """Test ML model trainer functionality."""

    @pytest.fixture
    def trainer(self, tmp_path):
        """Create ML model trainer for testing."""
        return MLModelTrainer(models_dir=tmp_path)

    def test_trainer_initialization(self, trainer, tmp_path):
        """Test ML model trainer initialization."""
        assert trainer.models_dir == tmp_path
        assert trainer.models_dir.exists()
        assert isinstance(trainer.data_generator, TrainingDataGenerator)
        assert trainer.trained_models == {}

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_error_classification_training(self, trainer):
        """Test error classification model training."""
        # Mock the training process
        with patch.object(trainer, "_train_error_classification_model") as mock_train:
            mock_train.return_value = {
                "random_forest": {
                    "metrics": {"accuracy": 0.85},
                    "model_path": "test_path",
                }
            }

            results = trainer._train_error_classification_model()

            assert "random_forest" in results
            assert "metrics" in results["random_forest"]

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_anomaly_detection_training(self, trainer):
        """Test anomaly detection model training."""
        with patch.object(trainer, "_train_anomaly_detection_model") as mock_train:
            mock_train.return_value = {
                "metrics": {"training_samples": 1000},
                "model_path": "test_path",
            }

            results = trainer._train_anomaly_detection_model()

            assert "metrics" in results
            assert "model_path" in results

    @patch("services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True)
    def test_recovery_recommendation_training(self, trainer):
        """Test recovery recommendation model training."""
        with patch.object(
            trainer, "_train_recovery_recommendation_model"
        ) as mock_train:
            mock_train.return_value = {
                "metrics": {"training_samples": 500},
                "model_path": "test_path",
            }

            results = trainer._train_recovery_recommendation_model()

            assert "metrics" in results
            assert "model_path" in results


@pytest.mark.integration
class TestMLIntegration:
    """Integration tests for ML models with ACGS-PGP v8."""

    def test_end_to_end_error_classification(self):
        """Test end-to-end error classification workflow."""
        # Generate training data
        generator = TrainingDataGenerator(seed=42)
        training_data = generator.generate_error_classification_data(n_samples=50)

        # Create and train model (mocked)
        with patch(
            "services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True
        ):
            model = ErrorClassificationModel("random_forest")

            # Mock the training process
            with patch.object(model, "model") as mock_model:
                with patch.object(model, "scaler") as mock_scaler:
                    with patch.object(model, "label_encoder") as mock_encoder:
                        # Setup mocks for successful training
                        mock_encoder.fit_transform.return_value = np.array([0, 1] * 25)
                        mock_encoder.inverse_transform.return_value = [
                            "SYSTEM_OVERLOAD"
                        ]
                        mock_scaler.fit_transform.return_value = training_data.features[
                            :40
                        ]
                        mock_scaler.transform.return_value = training_data.features[40:]
                        mock_model.fit.return_value = None
                        mock_model.predict.return_value = np.array([0] * 10)

                        # Train model
                        metrics = model.train(training_data)
                        assert model.is_trained

                        # Test prediction
                        mock_scaler.transform.return_value = np.array(
                            [[0.5] * len(training_data.feature_names)]
                        )
                        mock_model.predict.return_value = np.array([0])
                        mock_encoder.inverse_transform.return_value = [
                            "SYSTEM_OVERLOAD"
                        ]

                        error_data = {
                            "timestamp": datetime.now(),
                            "cpu_usage": 0.9,
                            "memory_usage": 0.8,
                            "error_code": 503,
                        }

                        predicted_class, confidence, info = model.predict(error_data)

                        assert isinstance(predicted_class, str)
                        assert isinstance(confidence, (int, float))
                        assert isinstance(info, dict)

    def test_ml_model_persistence(self, tmp_path):
        """Test ML model saving and loading."""
        model_path = tmp_path / "test_model.joblib"

        # Create and mock train a model
        with patch(
            "services.core.acgs_pgp_v8.src.sde.ml_models.SKLEARN_AVAILABLE", True
        ):
            model = ErrorClassificationModel("random_forest")

            # Mock training state
            model.is_trained = True
            model.feature_names = ["feature1", "feature2"]
            model.training_metrics = MagicMock()

            # Test saving (mocked)
            with patch(
                "services.core.acgs_pgp_v8.src.sde.ml_models.joblib"
            ) as mock_joblib:
                model.save_model(model_path)
                mock_joblib.dump.assert_called_once()

                # Test loading (mocked)
                mock_joblib.load.return_value = {
                    "model": MagicMock(),
                    "scaler": MagicMock(),
                    "label_encoder": MagicMock(),
                    "feature_names": ["feature1", "feature2"],
                    "model_type": "random_forest",
                    "training_metrics": MagicMock(),
                    "is_trained": True,
                }

                new_model = ErrorClassificationModel("random_forest")
                new_model.load_model(model_path)

                assert new_model.is_trained
                assert new_model.feature_names == ["feature1", "feature2"]
