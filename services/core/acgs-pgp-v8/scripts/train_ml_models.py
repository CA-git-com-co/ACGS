#!/usr/bin/env python3
"""
ML Model Training Script for ACGS-PGP v8

Trains and saves ML models for syndrome diagnosis including error classification,
anomaly detection, and recovery recommendation models.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sde.ml_models import MLModelTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("ml_training.log")],
)
logger = logging.getLogger(__name__)


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train ML models for ACGS-PGP v8")
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path("models"),
        help="Directory to save trained models",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=2000,
        help="Number of training samples to generate",
    )
    parser.add_argument(
        "--model-types",
        nargs="+",
        choices=[
            "error_classification",
            "anomaly_detection",
            "recovery_recommendation",
            "all",
        ],
        default=["all"],
        help="Types of models to train",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Run validation tests after training"
    )

    args = parser.parse_args()

    # Create models directory
    args.models_dir.mkdir(exist_ok=True)

    logger.info("Starting ML model training for ACGS-PGP v8")
    logger.info(f"Models directory: {args.models_dir}")
    logger.info(f"Training samples: {args.samples}")
    logger.info(f"Model types: {args.model_types}")

    try:
        # Initialize trainer
        trainer = MLModelTrainer(models_dir=args.models_dir)

        # Determine which models to train
        if "all" in args.model_types:
            model_types = [
                "error_classification",
                "anomaly_detection",
                "recovery_recommendation",
            ]
        else:
            model_types = args.model_types

        training_results = {}

        # Train error classification models
        if "error_classification" in model_types:
            logger.info("Training error classification models...")
            error_results = train_error_classification_models(trainer, args.samples)
            training_results["error_classification"] = error_results

        # Train anomaly detection model
        if "anomaly_detection" in model_types:
            logger.info("Training anomaly detection model...")
            anomaly_results = train_anomaly_detection_model(trainer)
            training_results["anomaly_detection"] = anomaly_results

        # Train recovery recommendation model
        if "recovery_recommendation" in model_types:
            logger.info("Training recovery recommendation model...")
            recovery_results = train_recovery_recommendation_model(
                trainer, args.samples
            )
            training_results["recovery_recommendation"] = recovery_results

        # Save training results
        results_file = args.models_dir / "training_results.json"
        with open(results_file, "w") as f:
            json.dump(training_results, f, indent=2, default=str)

        logger.info(f"Training results saved to {results_file}")

        # Run validation if requested
        if args.validate:
            logger.info("Running validation tests...")
            validation_results = run_validation_tests(args.models_dir)

            validation_file = args.models_dir / "validation_results.json"
            with open(validation_file, "w") as f:
                json.dump(validation_results, f, indent=2, default=str)

            logger.info(f"Validation results saved to {validation_file}")

        # Print summary
        print_training_summary(training_results)

        logger.info("ML model training completed successfully!")

    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


def train_error_classification_models(trainer: MLModelTrainer, n_samples: int) -> dict:
    """Train error classification models."""
    logger.info(f"Generating {n_samples} training samples for error classification...")

    # Generate training data
    training_data = trainer.data_generator.generate_error_classification_data(n_samples)

    results = {}

    # Train different model types
    model_types = ["random_forest", "gradient_boosting"]

    for model_type in model_types:
        try:
            logger.info(f"Training {model_type} error classification model...")

            from sde.ml_models import ErrorClassificationModel

            model = ErrorClassificationModel(model_type=model_type)
            metrics = model.train(training_data)

            # Save model
            model_path = (
                trainer.models_dir / f"error_classification_{model_type}.joblib"
            )
            model.save_model(model_path)

            results[model_type] = {
                "metrics": {
                    "accuracy": metrics.accuracy,
                    "precision": metrics.precision,
                    "recall": metrics.recall,
                    "f1_score": metrics.f1_score,
                    "training_time": metrics.training_time,
                    "cross_val_mean": float(
                        sum(metrics.cross_val_scores) / len(metrics.cross_val_scores)
                    ),
                    "cross_val_std": float(
                        sum(
                            (
                                x
                                - sum(metrics.cross_val_scores)
                                / len(metrics.cross_val_scores)
                            )
                            ** 2
                            for x in metrics.cross_val_scores
                        )
                        / len(metrics.cross_val_scores)
                    )
                    ** 0.5,
                },
                "model_path": str(model_path),
                "training_samples": n_samples,
                "feature_count": len(training_data.feature_names),
            }

            logger.info(
                f"{model_type} model trained with accuracy: {metrics.accuracy:.3f}"
            )

        except Exception as e:
            logger.error(f"Failed to train {model_type} model: {e}")
            results[model_type] = {"error": str(e)}

    return results


def train_anomaly_detection_model(trainer: MLModelTrainer) -> dict:
    """Train anomaly detection model."""
    try:
        import numpy as np
        from sde.ml_models import AnomalyDetectionModel

        # Generate normal system behavior data
        logger.info("Generating normal system behavior data...")
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

        # Train model
        model = AnomalyDetectionModel(contamination=0.1)
        metrics = model.train(normal_data)

        # Save model
        import joblib

        model_path = trainer.models_dir / "anomaly_detection.joblib"
        joblib.dump(model, model_path)

        return {
            "metrics": metrics,
            "model_path": str(model_path),
            "training_samples": len(normal_data),
        }

    except Exception as e:
        logger.error(f"Failed to train anomaly detection model: {e}")
        return {"error": str(e)}


def train_recovery_recommendation_model(
    trainer: MLModelTrainer, n_samples: int
) -> dict:
    """Train recovery recommendation model."""
    try:
        from sde.ml_models import RecoveryRecommendationModel

        # Generate training data
        logger.info(
            f"Generating {n_samples} training samples for recovery recommendations..."
        )
        error_descriptions, recovery_strategies = (
            trainer.data_generator.generate_recovery_recommendation_data(n_samples)
        )

        # Train model
        model = RecoveryRecommendationModel()
        metrics = model.train(error_descriptions, recovery_strategies)

        # Save model
        import joblib

        model_path = trainer.models_dir / "recovery_recommendation.joblib"
        joblib.dump(model, model_path)

        return {
            "metrics": metrics,
            "model_path": str(model_path),
            "training_samples": n_samples,
        }

    except Exception as e:
        logger.error(f"Failed to train recovery recommendation model: {e}")
        return {"error": str(e)}


def run_validation_tests(models_dir: Path) -> dict:
    """Run validation tests on trained models."""
    validation_results = {}

    try:
        # Test error classification model
        logger.info("Validating error classification model...")
        error_validation = validate_error_classification_model(models_dir)
        validation_results["error_classification"] = error_validation

        # Test anomaly detection model
        logger.info("Validating anomaly detection model...")
        anomaly_validation = validate_anomaly_detection_model(models_dir)
        validation_results["anomaly_detection"] = anomaly_validation

        # Test recovery recommendation model
        logger.info("Validating recovery recommendation model...")
        recovery_validation = validate_recovery_recommendation_model(models_dir)
        validation_results["recovery_recommendation"] = recovery_validation

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        validation_results["error"] = str(e)

    return validation_results


def validate_error_classification_model(models_dir: Path) -> dict:
    """Validate error classification model."""
    try:
        from sde.ml_models import ErrorClassificationModel

        # Load model
        model_path = models_dir / "error_classification_random_forest.joblib"
        if not model_path.exists():
            return {"error": "Model file not found"}

        model = ErrorClassificationModel("random_forest")
        model.load_model(model_path)

        # Test prediction
        test_error_data = {
            "timestamp": datetime.now(),
            "cpu_usage": 0.9,
            "memory_usage": 0.8,
            "response_time_ms": 2000,
            "error_code": 503,
            "constitutional_compliance_score": 0.85,
        }

        predicted_class, confidence, additional_info = model.predict(test_error_data)

        return {
            "status": "success",
            "test_prediction": {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "model_type": additional_info.get("model_type"),
            },
        }

    except Exception as e:
        return {"error": str(e)}


def validate_anomaly_detection_model(models_dir: Path) -> dict:
    """Validate anomaly detection model."""
    try:
        import joblib
        import numpy as np

        # Load model
        model_path = models_dir / "anomaly_detection.joblib"
        if not model_path.exists():
            return {"error": "Model file not found"}

        model = joblib.load(model_path)

        # Test normal data point
        normal_data = np.array([[0.5, 0.4, 0.3, 50, 25, 300, 0.9]])
        is_anomaly, score = model.detect_anomaly(normal_data)

        return {
            "status": "success",
            "test_normal_data": {"is_anomaly": is_anomaly, "anomaly_score": score},
        }

    except Exception as e:
        return {"error": str(e)}


def validate_recovery_recommendation_model(models_dir: Path) -> dict:
    """Validate recovery recommendation model."""
    try:
        import joblib

        # Load model
        model_path = models_dir / "recovery_recommendation.joblib"
        if not model_path.exists():
            return {"error": "Model file not found"}

        model = joblib.load(model_path)

        # Test recommendation
        test_error = "High CPU usage detected at 95%"
        strategy, confidence = model.recommend_recovery(test_error)

        return {
            "status": "success",
            "test_recommendation": {
                "error_description": test_error,
                "recommended_strategy": strategy,
                "confidence": confidence,
            },
        }

    except Exception as e:
        return {"error": str(e)}


def print_training_summary(results: dict):
    """Print training summary."""
    print("\n" + "=" * 60)
    print("ACGS-PGP v8 ML Model Training Summary")
    print("=" * 60)

    for model_category, category_results in results.items():
        print(f"\n{model_category.upper()}:")

        if isinstance(category_results, dict) and "error" in category_results:
            print(f"  ❌ Training failed: {category_results['error']}")
        else:
            for model_type, model_results in category_results.items():
                if "error" in model_results:
                    print(f"  ❌ {model_type}: {model_results['error']}")
                else:
                    metrics = model_results.get("metrics", {})
                    accuracy = metrics.get("accuracy", "N/A")
                    print(
                        f"  ✅ {model_type}: Accuracy {accuracy:.3f}"
                        if isinstance(accuracy, float)
                        else f"  ✅ {model_type}: {accuracy}"
                    )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
