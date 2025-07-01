"""
Comprehensive MLOps Integration Tests

Tests for the complete MLOps framework including model versioning,
Git integration, artifact storage, and deployment pipelines.

This test suite validates the MLOps system integration with
ACGS-PGP constitutional compliance requirements.
"""

import unittest
import tempfile
import shutil
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch

from .mlops_manager import MLOpsManager, MLOpsConfig, DeploymentResult
from .model_versioning import VersionPolicy, SemanticVersion
from .deployment_pipeline import DeploymentStatus


class TestMLOpsIntegration(unittest.TestCase):
    """Test MLOps system integration."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

        # Create test configuration
        self.config = MLOpsConfig(
            storage_root=str(self.test_path / "mlops"),
            model_versions_path=str(self.test_path / "mlops" / "versions"),
            artifacts_path=str(self.test_path / "mlops" / "artifacts"),
            deployments_path=str(self.test_path / "mlops" / "deployments"),
            git_repo_path=str(self.test_path),
            constitutional_hash="cdd01ef066bc6cf2",
        )

        # Initialize Git repository
        self._init_test_git_repo()

        # Create test model and config files
        self.model_file = self.test_path / "test_model.pkl"
        self.config_file = self.test_path / "test_config.json"

        self._create_test_files()

        # Initialize MLOps manager
        self.mlops = MLOpsManager(self.config)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)

    def _init_test_git_repo(self):
        """Initialize test Git repository."""
        import subprocess

        # Initialize Git repo
        subprocess.run(["git", "init"], cwd=self.test_path, capture_output=True)
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=self.test_path,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=self.test_path,
            capture_output=True,
        )

        # Create initial commit
        test_file = self.test_path / "README.md"
        test_file.write_text("# Test Repository")

        subprocess.run(
            ["git", "add", "README.md"], cwd=self.test_path, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=self.test_path,
            capture_output=True,
        )

    def _create_test_files(self):
        """Create test model and configuration files."""
        # Create mock model file
        self.model_file.write_text("Mock model data")

        # Create test configuration
        config_data = {
            "model_type": "test_model",
            "parameters": {"learning_rate": 0.001, "batch_size": 32},
            "constitutional_hash": "cdd01ef066bc6cf2",
        }

        self.config_file.write_text(json.dumps(config_data, indent=2))

    def test_model_version_creation(self):
        """Test model version creation with MLOps integration."""

        performance_metrics = {
            "accuracy": 0.92,
            "precision": 0.89,
            "recall": 0.94,
            "constitutional_compliance": 0.97,
            "response_time_ms": 450,
        }

        # Create model version
        model_version = self.mlops.create_model_version(
            model_name="test_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=performance_metrics,
            version_policy=VersionPolicy.MINOR,
        )

        # Validate model version
        self.assertIsNotNone(model_version)
        self.assertEqual(model_version.model_name, "test_model")
        self.assertEqual(model_version.constitutional_hash, "cdd01ef066bc6cf2")
        self.assertEqual(model_version.constitutional_compliance_score, 0.97)
        self.assertGreater(model_version.version.minor, 0)

        # Validate Git integration
        self.assertIsNotNone(model_version.git_commit_hash)
        self.assertIsNotNone(model_version.git_branch)

        # Validate artifacts were stored
        artifacts = self.mlops.artifact_manager.storage.list_artifacts(
            name="test_model"
        )
        self.assertGreater(len(artifacts), 0)

    def test_constitutional_compliance_validation(self):
        """Test constitutional compliance validation."""

        # Test with low constitutional compliance
        low_compliance_metrics = {
            "accuracy": 0.85,
            "constitutional_compliance": 0.80,  # Below threshold
        }

        # Should still create version but with warning
        model_version = self.mlops.create_model_version(
            model_name="low_compliance_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=low_compliance_metrics,
        )

        self.assertEqual(model_version.constitutional_compliance_score, 0.80)

        # Test deployment should fail due to low compliance
        with self.assertRaises(Exception):
            self.mlops.deploy_model(
                model_name="low_compliance_model",
                model_version=str(model_version.version),
            )

    def test_deployment_pipeline(self):
        """Test complete deployment pipeline."""

        # Create model version with good metrics
        performance_metrics = {
            "accuracy": 0.92,
            "precision": 0.89,
            "recall": 0.94,
            "constitutional_compliance": 0.97,
            "response_time_ms": 450,
        }

        model_version = self.mlops.create_model_version(
            model_name="deployment_test_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=performance_metrics,
        )

        # Mock deployment validation to pass
        with (
            patch.object(
                self.mlops.deployment_pipeline.validator,
                "_validate_constitutional_compliance",
            ) as mock_constitutional,
            patch.object(
                self.mlops.deployment_pipeline.validator,
                "_validate_performance_metrics",
            ) as mock_performance,
            patch.object(
                self.mlops.deployment_pipeline.validator, "_validate_response_time"
            ) as mock_response_time,
            patch.object(
                self.mlops.deployment_pipeline.validator, "_validate_health_check"
            ) as mock_health,
            patch.object(
                self.mlops.deployment_pipeline.validator, "_validate_integration_test"
            ) as mock_integration,
        ):

            # Configure mocks to return passing results
            from .deployment_pipeline import ValidationResult

            mock_constitutional.return_value = ValidationResult(
                "constitutional_compliance", True, 0.97, {}
            )
            mock_performance.return_value = ValidationResult(
                "performance_metrics", True, 0.92, {}
            )
            mock_response_time.return_value = ValidationResult(
                "response_time", True, 0.95, {}
            )
            mock_health.return_value = ValidationResult("health_check", True, 1.0, {})
            mock_integration.return_value = ValidationResult(
                "integration_test", True, 1.0, {}
            )

            # Deploy model
            deployment_result = self.mlops.deploy_model(
                model_name="deployment_test_model",
                model_version=str(model_version.version),
            )

            # Validate deployment result
            self.assertIsInstance(deployment_result, DeploymentResult)
            self.assertTrue(deployment_result.staging_validation_passed)
            self.assertTrue(deployment_result.production_promotion_success)
            self.assertEqual(
                deployment_result.deployment_status, DeploymentStatus.DEPLOYED
            )
            self.assertTrue(deployment_result.constitutional_compliance_verified)

    def test_model_rollback(self):
        """Test model rollback functionality."""

        # Create first model version
        performance_metrics_v1 = {"accuracy": 0.90, "constitutional_compliance": 0.96}

        model_v1 = self.mlops.create_model_version(
            model_name="rollback_test_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=performance_metrics_v1,
        )

        # Promote to production
        self.mlops.version_manager.promote_to_production(str(model_v1.version))

        # Create second model version
        performance_metrics_v2 = {"accuracy": 0.92, "constitutional_compliance": 0.97}

        model_v2 = self.mlops.create_model_version(
            model_name="rollback_test_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=performance_metrics_v2,
            parent_version=str(model_v1.version),
        )

        # Promote v2 to production
        self.mlops.version_manager.promote_to_production(str(model_v2.version))

        # Verify v2 is in production
        production_version = self.mlops.version_manager.get_production_version(
            "rollback_test_model"
        )
        self.assertEqual(production_version.version, model_v2.version)

        # Rollback to v1
        rollback_success = self.mlops.rollback_model(
            "rollback_test_model", "Performance degradation detected"
        )

        self.assertTrue(rollback_success)

        # Verify v1 is back in production
        production_version = self.mlops.version_manager.get_production_version(
            "rollback_test_model"
        )
        self.assertEqual(production_version.version, model_v1.version)

    def test_artifact_lineage_tracking(self):
        """Test artifact lineage tracking."""

        # Create parent model
        parent_metrics = {"accuracy": 0.88, "constitutional_compliance": 0.95}

        parent_model = self.mlops.create_model_version(
            model_name="lineage_parent_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=parent_metrics,
        )

        # Create child model with lineage
        child_metrics = {"accuracy": 0.91, "constitutional_compliance": 0.96}

        child_model = self.mlops.create_model_version(
            model_name="lineage_child_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=child_metrics,
            parent_version=str(parent_model.version),
        )

        # Verify lineage
        self.assertEqual(child_model.parent_version, str(parent_model.version))

        # Test artifact lineage
        child_artifacts = self.mlops.artifact_manager.storage.list_artifacts(
            name="lineage_child_model"
        )

        if child_artifacts:
            lineage = self.mlops.artifact_manager.lineage.trace_lineage(
                child_artifacts[0].artifact_id
            )

            self.assertIsNotNone(lineage)
            self.assertEqual(lineage["artifact_id"], child_artifacts[0].artifact_id)

    def test_git_integration(self):
        """Test Git integration functionality."""

        # Test Git tracker
        repo_info = self.mlops.git_tracker.git.get_repository_info()

        self.assertTrue(repo_info["constitutional_hash_verified"])
        self.assertEqual(repo_info["constitutional_hash"], "cdd01ef066bc6cf2")
        self.assertTrue(repo_info["is_clean"])

        # Test deployment readiness validation
        readiness = self.mlops.git_tracker.validate_deployment_readiness()

        self.assertIsInstance(readiness, dict)
        self.assertIn("is_ready", readiness)
        self.assertIn("constitutional_hash_verified", readiness)

    def test_mlops_dashboard(self):
        """Test MLOps dashboard data generation."""

        # Create some test data
        performance_metrics = {"accuracy": 0.90, "constitutional_compliance": 0.96}

        self.mlops.create_model_version(
            model_name="dashboard_test_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=performance_metrics,
        )

        # Get dashboard data
        dashboard = self.mlops.get_mlops_dashboard()

        # Validate dashboard structure
        self.assertIn("mlops_overview", dashboard)
        self.assertIn("version_statistics", dashboard)
        self.assertIn("artifact_statistics", dashboard)
        self.assertIn("pipeline_statistics", dashboard)
        self.assertIn("recent_versions", dashboard)
        self.assertIn("recent_deployments", dashboard)
        self.assertIn("system_health", dashboard)

        # Validate constitutional compliance
        self.assertTrue(dashboard["mlops_overview"]["constitutional_hash_verified"])
        self.assertEqual(
            dashboard["mlops_overview"]["constitutional_hash"], "cdd01ef066bc6cf2"
        )

        # Validate system health
        system_health = dashboard["system_health"]
        self.assertTrue(system_health["git_integration"])
        self.assertTrue(system_health["artifact_storage"])
        self.assertTrue(system_health["deployment_pipeline"])
        self.assertTrue(system_health["constitutional_compliance"])

    def test_performance_targets_validation(self):
        """Test performance targets validation."""

        # Test with metrics meeting all targets
        good_metrics = {
            "accuracy": 0.92,
            "constitutional_compliance": 0.97,
            "response_time_ms": 1500,  # Below 2000ms target
            "cost_savings": 0.75,  # Above 0.74 target
        }

        model_version = self.mlops.create_model_version(
            model_name="performance_test_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=good_metrics,
        )

        # Validate performance targets
        targets = self.config.performance_targets

        self.assertGreaterEqual(
            good_metrics["constitutional_compliance"],
            targets["constitutional_compliance"],
        )
        self.assertLessEqual(
            good_metrics["response_time_ms"], targets["response_time_ms"]
        )
        self.assertGreaterEqual(good_metrics["accuracy"], targets["model_accuracy"])

    def test_constitutional_hash_integrity(self):
        """Test constitutional hash integrity throughout the system."""

        # Verify all components use correct constitutional hash
        self.assertEqual(self.mlops.config.constitutional_hash, "cdd01ef066bc6cf2")
        self.assertEqual(
            self.mlops.version_manager.constitutional_hash, "cdd01ef066bc6cf2"
        )
        self.assertEqual(self.mlops.git_tracker.constitutional_hash, "cdd01ef066bc6cf2")
        self.assertEqual(
            self.mlops.artifact_manager.constitutional_hash, "cdd01ef066bc6cf2"
        )
        self.assertEqual(
            self.mlops.deployment_pipeline.constitutional_hash, "cdd01ef066bc6cf2"
        )

        # Create model version and verify hash propagation
        performance_metrics = {"accuracy": 0.90, "constitutional_compliance": 0.96}

        model_version = self.mlops.create_model_version(
            model_name="hash_test_model",
            model_path=self.model_file,
            config_path=self.config_file,
            performance_metrics=performance_metrics,
        )

        self.assertEqual(model_version.constitutional_hash, "cdd01ef066bc6cf2")


if __name__ == "__main__":
    unittest.main()
