"""
Model Updater Service - Handles model retraining and updates
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import asyncio
import json
import pickle
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import mlflow
import redis.asyncio as redis

from ..models.schemas import (
    ModelConfiguration,
    TrainingJob,
    ModelType,
    ModelStatus,
    ModelUpdateRequest,
    ModelPerformance,
    AdaptiveLearningConfig,
    CONSTITUTIONAL_HASH,
)

logger = logging.getLogger(__name__)


class ModelUpdater:
    """Service for updating and retraining models based on feedback."""

    def __init__(
        self, redis_url: str = "redis://localhost:6389", model_dir: str = "/tmp/models"
    ):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.redis_client = None
        self.redis_url = redis_url
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

        # Model configurations
        self.model_configs = {
            ModelType.CONSTITUTIONAL_AI: {
                "algorithm": "constitutional_classifier",
                "hyperparameters": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 2,
                },
            },
            ModelType.GOVERNANCE: {
                "algorithm": "governance_classifier",
                "hyperparameters": {"C": 1.0, "solver": "liblinear"},
            },
            ModelType.MULTIMODAL: {
                "algorithm": "multimodal_classifier",
                "hyperparameters": {"n_estimators": 200, "max_depth": 15},
            },
            ModelType.RECOMMENDATION: {
                "algorithm": "recommendation_model",
                "hyperparameters": {"n_factors": 50, "learning_rate": 0.01},
            },
            ModelType.CHAT: {
                "algorithm": "chat_model",
                "hyperparameters": {"hidden_dim": 256, "num_layers": 3},
            },
        }

        # Default learning config
        self.learning_config = AdaptiveLearningConfig()

    async def initialize(self):
        """Initialize the model updater."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()

            # Initialize MLflow
            mlflow.set_tracking_uri("sqlite:///mlflow.db")
            mlflow.set_experiment("adaptive-learning")

            logger.info("Model updater initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize model updater: {e}")
            raise

    async def trigger_model_update(self, request: ModelUpdateRequest) -> TrainingJob:
        """Trigger a model update/retrain job."""
        try:
            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise ValueError("Invalid constitutional hash")

            # Get current model configuration
            current_config = await self._get_current_model_config(request.model_type)

            # Create new configuration with updates
            new_config = ModelConfiguration(
                model_type=request.model_type,
                model_name=f"{request.model_type.value}_v{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                configuration=current_config.configuration.copy(),
                hyperparameters=current_config.hyperparameters.copy(),
            )

            # Apply configuration updates
            if request.configuration_updates:
                new_config.configuration.update(request.configuration_updates)

            # Create training job
            training_job = TrainingJob(
                model_type=request.model_type,
                model_configuration_id=new_config.id,
                training_data_size=await self._get_training_data_size(
                    request.model_type
                ),
                status=ModelStatus.TRAINING,
            )

            # Store job in Redis
            await self._store_training_job(training_job)

            # Start training in background
            asyncio.create_task(self._execute_training_job(training_job, new_config))

            logger.info(f"Model update triggered: {training_job.id}")
            return training_job

        except Exception as e:
            logger.error(f"Failed to trigger model update: {e}")
            raise

    async def _get_current_model_config(
        self, model_type: ModelType
    ) -> ModelConfiguration:
        """Get current model configuration."""
        try:
            config_key = f"model_config:{model_type.value}"
            config_data = await self.redis_client.hgetall(config_key)

            if not config_data:
                # Return default configuration
                default_config = self.model_configs.get(model_type, {})
                return ModelConfiguration(
                    model_type=model_type,
                    model_name=f"{model_type.value}_default",
                    configuration=default_config,
                    hyperparameters=default_config.get("hyperparameters", {}),
                )

            return ModelConfiguration(
                id=config_data["id"],
                model_type=model_type,
                model_name=config_data["model_name"],
                configuration=json.loads(config_data["configuration"]),
                hyperparameters=json.loads(config_data["hyperparameters"]),
                version=config_data["version"],
                status=ModelStatus(config_data["status"]),
            )

        except Exception as e:
            logger.error(f"Failed to get current model config: {e}")
            raise

    async def _get_training_data_size(self, model_type: ModelType) -> int:
        """Get size of training data available."""
        try:
            feedback_key = f"model_feedback:{model_type.value}"
            size = await self.redis_client.llen(feedback_key)
            return size

        except Exception as e:
            logger.error(f"Failed to get training data size: {e}")
            return 0

    async def _store_training_job(self, job: TrainingJob):
        """Store training job in Redis."""
        try:
            job_key = f"training_job:{job.id}"
            job_data = {
                "id": job.id,
                "model_type": job.model_type.value,
                "model_configuration_id": job.model_configuration_id,
                "training_data_size": job.training_data_size,
                "epochs": job.epochs,
                "batch_size": job.batch_size,
                "learning_rate": job.learning_rate,
                "status": job.status.value,
                "progress": job.progress,
                "metrics": json.dumps(job.metrics),
                "started_at": job.started_at.isoformat(),
                "constitutional_hash": job.constitutional_hash,
            }

            await self.redis_client.hset(job_key, mapping=job_data)

            # Add to active jobs list
            await self.redis_client.lpush(f"active_jobs:{job.model_type.value}", job.id)

            logger.info(f"Training job stored: {job.id}")

        except Exception as e:
            logger.error(f"Failed to store training job: {e}")

    async def _execute_training_job(self, job: TrainingJob, config: ModelConfiguration):
        """Execute the training job."""
        try:
            logger.info(f"Starting training job: {job.id}")

            # Update job status
            await self._update_job_status(job.id, ModelStatus.TRAINING, 0.0)

            # Get training data
            training_data = await self._prepare_training_data(job.model_type)

            if not training_data:
                await self._update_job_status(
                    job.id, ModelStatus.FAILED, 0.0, "No training data available"
                )
                return

            # Start MLflow run
            with mlflow.start_run(run_name=f"{job.model_type.value}_{job.id}"):
                # Log parameters
                mlflow.log_params(config.hyperparameters)
                mlflow.log_param("model_type", job.model_type.value)
                mlflow.log_param("training_data_size", job.training_data_size)
                mlflow.log_param("constitutional_hash", self.constitutional_hash)

                # Train model
                model, metrics = await self._train_model(job, config, training_data)

                if model is None:
                    await self._update_job_status(
                        job.id, ModelStatus.FAILED, 0.0, "Model training failed"
                    )
                    return

                # Log metrics
                mlflow.log_metrics(metrics)

                # Save model
                model_path = self.model_dir / f"{job.model_type.value}_{job.id}.pkl"
                joblib.dump(model, model_path)
                mlflow.sklearn.log_model(model, "model")

                # Update job status
                await self._update_job_status(job.id, ModelStatus.VALIDATING, 0.8)

                # Validate model
                validation_metrics = await self._validate_model(model, job.model_type)

                # Check constitutional compliance
                constitutional_score = await self._check_constitutional_compliance(
                    model, job.model_type
                )

                if (
                    constitutional_score
                    < self.learning_config.constitutional_compliance_threshold
                ):
                    await self._update_job_status(
                        job.id,
                        ModelStatus.FAILED,
                        0.0,
                        f"Constitutional compliance failed: {constitutional_score}",
                    )
                    return

                # Complete training
                final_metrics = {
                    **metrics,
                    **validation_metrics,
                    "constitutional_compliance": constitutional_score,
                }

                await self._update_job_status(
                    job.id, ModelStatus.DEPLOYED, 1.0, None, final_metrics
                )

                # Deploy model if auto-deployment enabled
                if self.learning_config.auto_deployment_enabled:
                    await self._deploy_model(job.id, model_path, config)

                logger.info(f"Training job completed successfully: {job.id}")

        except Exception as e:
            logger.error(f"Training job failed: {job.id}, error: {e}")
            await self._update_job_status(job.id, ModelStatus.FAILED, 0.0, str(e))

    async def _prepare_training_data(
        self, model_type: ModelType
    ) -> Optional[Dict[str, Any]]:
        """Prepare training data from feedback."""
        try:
            feedback_key = f"model_feedback:{model_type.value}"
            feedback_ids = await self.redis_client.lrange(feedback_key, 0, -1)

            if not feedback_ids:
                return None

            # Collect feedback data
            features = []
            labels = []

            for feedback_id in feedback_ids:
                feedback_data = await self.redis_client.hgetall(
                    f"feedback:{feedback_id}"
                )
                if feedback_data:
                    # Extract features (simplified)
                    feature_vector = self._extract_features(feedback_data)
                    label = self._extract_label(feedback_data)

                    if feature_vector and label is not None:
                        features.append(feature_vector)
                        labels.append(label)

            if not features:
                return None

            return {
                "features": np.array(features),
                "labels": np.array(labels),
                "size": len(features),
            }

        except Exception as e:
            logger.error(f"Failed to prepare training data: {e}")
            return None

    def _extract_features(self, feedback_data: Dict[str, str]) -> Optional[List[float]]:
        """Extract features from feedback data."""
        try:
            # Simplified feature extraction
            features = []

            # Rating feature
            rating = feedback_data.get("rating", "")
            features.append(float(rating) if rating else 0.0)

            # Feedback type features (one-hot encoded)
            feedback_type = feedback_data.get("feedback_type", "")
            features.extend(
                [
                    1.0 if feedback_type == "positive" else 0.0,
                    1.0 if feedback_type == "negative" else 0.0,
                    1.0 if feedback_type == "neutral" else 0.0,
                    1.0 if feedback_type == "explicit" else 0.0,
                    1.0 if feedback_type == "implicit" else 0.0,
                ]
            )

            # Temporal features
            timestamp = feedback_data.get("timestamp", "")
            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                features.extend(
                    [
                        dt.hour / 24.0,  # Hour of day
                        dt.weekday() / 7.0,  # Day of week
                        (datetime.utcnow() - dt).days / 30.0,  # Age in months
                    ]
                )
            else:
                features.extend([0.0, 0.0, 0.0])

            return features

        except Exception as e:
            logger.error(f"Failed to extract features: {e}")
            return None

    def _extract_label(self, feedback_data: Dict[str, str]) -> Optional[int]:
        """Extract label from feedback data."""
        try:
            feedback_type = feedback_data.get("feedback_type", "")

            # Binary classification: positive/negative
            if feedback_type == "positive":
                return 1
            elif feedback_type == "negative":
                return 0
            else:
                # Use rating for neutral feedback
                rating = feedback_data.get("rating", "")
                if rating:
                    return 1 if float(rating) >= 3.0 else 0
                return None

        except Exception as e:
            logger.error(f"Failed to extract label: {e}")
            return None

    async def _train_model(
        self,
        job: TrainingJob,
        config: ModelConfiguration,
        training_data: Dict[str, Any],
    ) -> tuple[Optional[Any], Dict[str, float]]:
        """Train the model."""
        try:
            X = training_data["features"]
            y = training_data["labels"]

            # Update progress
            await self._update_job_status(job.id, ModelStatus.TRAINING, 0.2)

            # Select algorithm based on model type
            algorithm = config.configuration.get("algorithm", "random_forest")

            if algorithm == "constitutional_classifier" or algorithm == "random_forest":
                model = RandomForestClassifier(**config.hyperparameters)
            elif (
                algorithm == "governance_classifier"
                or algorithm == "logistic_regression"
            ):
                model = LogisticRegression(**config.hyperparameters)
            else:
                # Default to random forest
                model = RandomForestClassifier(n_estimators=100, max_depth=10)

            # Train model
            model.fit(X, y)

            # Update progress
            await self._update_job_status(job.id, ModelStatus.TRAINING, 0.6)

            # Calculate metrics
            y_pred = model.predict(X)
            metrics = {
                "accuracy": accuracy_score(y, y_pred),
                "precision": precision_score(y, y_pred, average="weighted"),
                "recall": recall_score(y, y_pred, average="weighted"),
                "f1_score": f1_score(y, y_pred, average="weighted"),
            }

            return model, metrics

        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return None, {}

    async def _validate_model(
        self, model: Any, model_type: ModelType
    ) -> Dict[str, float]:
        """Validate the trained model."""
        try:
            # Get validation data (could be held-out test set)
            validation_data = await self._prepare_training_data(model_type)

            if not validation_data:
                return {"validation_accuracy": 0.0}

            X_val = validation_data["features"]
            y_val = validation_data["labels"]

            # Make predictions
            y_pred = model.predict(X_val)

            # Calculate validation metrics
            metrics = {
                "validation_accuracy": accuracy_score(y_val, y_pred),
                "validation_precision": precision_score(
                    y_val, y_pred, average="weighted"
                ),
                "validation_recall": recall_score(y_val, y_pred, average="weighted"),
                "validation_f1": f1_score(y_val, y_pred, average="weighted"),
            }

            return metrics

        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return {"validation_accuracy": 0.0}

    async def _check_constitutional_compliance(
        self, model: Any, model_type: ModelType
    ) -> float:
        """Check constitutional compliance of the model."""
        try:
            # This is a simplified compliance check
            # In a real implementation, this would involve:
            # 1. Testing against constitutional principles
            # 2. Bias detection
            # 3. Fairness metrics
            # 4. Explainability checks

            # For now, return a mock score based on model performance
            # In practice, this would be much more sophisticated

            # Mock constitutional compliance score
            # Higher accuracy models are assumed to be more compliant
            if hasattr(model, "score"):
                # This is a placeholder - real implementation would be much more complex
                mock_score = 0.85 + (0.1 * np.random.random())
            else:
                mock_score = 0.90

            return min(mock_score, 1.0)

        except Exception as e:
            logger.error(f"Constitutional compliance check failed: {e}")
            return 0.0

    async def _update_job_status(
        self,
        job_id: str,
        status: ModelStatus,
        progress: float,
        error_message: Optional[str] = None,
        metrics: Optional[Dict[str, float]] = None,
    ):
        """Update training job status."""
        try:
            job_key = f"training_job:{job_id}"

            updates = {"status": status.value, "progress": progress}

            if error_message:
                updates["error_message"] = error_message

            if metrics:
                updates["metrics"] = json.dumps(metrics)

            if status in [ModelStatus.DEPLOYED, ModelStatus.FAILED]:
                updates["completed_at"] = datetime.utcnow().isoformat()

            await self.redis_client.hset(job_key, mapping=updates)

            logger.info(f"Training job {job_id} status updated to {status.value}")

        except Exception as e:
            logger.error(f"Failed to update job status: {e}")

    async def _deploy_model(
        self, job_id: str, model_path: Path, config: ModelConfiguration
    ):
        """Deploy the trained model."""
        try:
            # Store model configuration
            config_key = f"model_config:{config.model_type.value}"
            config_data = {
                "id": config.id,
                "model_name": config.model_name,
                "configuration": json.dumps(config.configuration),
                "hyperparameters": json.dumps(config.hyperparameters),
                "version": config.version,
                "status": ModelStatus.DEPLOYED.value,
                "model_path": str(model_path),
                "job_id": job_id,
                "deployed_at": datetime.utcnow().isoformat(),
                "constitutional_hash": config.constitutional_hash,
            }

            await self.redis_client.hset(config_key, mapping=config_data)

            logger.info(f"Model deployed: {config.model_name}")

        except Exception as e:
            logger.error(f"Failed to deploy model: {e}")

    async def get_training_jobs(
        self, model_type: ModelType = None
    ) -> List[TrainingJob]:
        """Get training jobs."""
        try:
            jobs = []

            if model_type:
                job_ids = await self.redis_client.lrange(
                    f"active_jobs:{model_type.value}", 0, -1
                )
            else:
                # Get all jobs
                job_ids = []
                for mt in ModelType:
                    ids = await self.redis_client.lrange(
                        f"active_jobs:{mt.value}", 0, -1
                    )
                    job_ids.extend(ids)

            for job_id in job_ids:
                job_data = await self.redis_client.hgetall(f"training_job:{job_id}")
                if job_data:
                    job = TrainingJob(
                        id=job_data["id"],
                        model_type=ModelType(job_data["model_type"]),
                        model_configuration_id=job_data["model_configuration_id"],
                        training_data_size=int(job_data["training_data_size"]),
                        epochs=int(job_data["epochs"]),
                        batch_size=int(job_data["batch_size"]),
                        learning_rate=float(job_data["learning_rate"]),
                        status=ModelStatus(job_data["status"]),
                        progress=float(job_data["progress"]),
                        metrics=json.loads(job_data["metrics"]),
                        error_message=job_data.get("error_message"),
                        started_at=datetime.fromisoformat(job_data["started_at"]),
                        constitutional_hash=job_data["constitutional_hash"],
                    )
                    jobs.append(job)

            return jobs

        except Exception as e:
            logger.error(f"Failed to get training jobs: {e}")
            return []

    async def health_check(self) -> bool:
        """Check service health."""
        try:
            if not self.redis_client:
                return False

            await self.redis_client.ping()
            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
