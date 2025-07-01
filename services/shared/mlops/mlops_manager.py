"""
MLOps Manager

Main orchestration class for MLOps operations in the ACGS-PGP system.
Coordinates model versioning, Git integration, artifact storage, and
deployment pipelines with constitutional compliance.

This module provides a unified interface for all MLOps operations
while maintaining integration with existing ACGS-PGP services.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .artifact_storage import ArtifactManager
from .deployment_pipeline import DeploymentPipeline, DeploymentStatus
from .git_integration import GitTracker
from .model_versioning import MLOpsModelVersion, ModelVersionManager, VersionPolicy

logger = logging.getLogger(__name__)


class MLOpsError(Exception):
    """Raised when MLOps operations fail."""

    pass


@dataclass
class MLOpsConfig:
    """Configuration for MLOps operations."""

    # Storage paths
    storage_root: str = "./mlops"
    model_versions_path: str = "./mlops/versions"
    artifacts_path: str = "./mlops/artifacts"
    deployments_path: str = "./mlops/deployments"

    # Git configuration
    git_repo_path: str = "."
    auto_git_tagging: bool = True

    # Artifact storage
    enable_compression: bool = True
    artifact_retention_days: int = 90

    # Deployment configuration
    staging_validation_config: dict[str, Any] = field(
        default_factory=lambda: {
            "constitutional_compliance": {"threshold": 0.95},
            "performance_metrics": {
                "thresholds": {
                    "accuracy": 0.85,
                    "precision": 0.80,
                    "recall": 0.80,
                    "f1_score": 0.80,
                }
            },
            "response_time": {"threshold_seconds": 2.0, "p95_threshold_seconds": 1.5},
            "health_check": {"max_memory_mb": 1024, "max_cpu_percent": 80.0},
            "integration_test": {},
        }
    )

    production_promotion_config: dict[str, Any] = field(
        default_factory=lambda: {
            "blue_green_deployment": True,
            "traffic_shift_percentage": [10, 50, 100],
            "monitoring_duration_minutes": 30,
            "rollback_threshold": 0.05,
        }
    )

    # Constitutional compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Performance targets
    performance_targets: dict[str, float] = field(
        default_factory=lambda: {
            "response_time_ms": 2000,
            "constitutional_compliance": 0.95,
            "cost_savings": 0.74,
            "availability": 0.999,
            "model_accuracy": 0.90,
        }
    )


@dataclass
class DeploymentResult:
    """Result of a complete deployment operation."""

    deployment_id: str
    model_version: MLOpsModelVersion
    artifact_ids: dict[str, str]
    git_tag: str
    deployment_status: DeploymentStatus

    # Validation results
    staging_validation_passed: bool
    production_promotion_success: bool

    # Timestamps
    started_at: datetime
    completed_at: datetime | None = None

    # Performance metrics
    final_performance_metrics: dict[str, float] = field(default_factory=dict)

    # Constitutional compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"
    constitutional_compliance_verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "deployment_id": self.deployment_id,
            "model_version": self.model_version.to_dict(),
            "artifact_ids": self.artifact_ids,
            "git_tag": self.git_tag,
            "deployment_status": self.deployment_status.value,
            "staging_validation_passed": self.staging_validation_passed,
            "production_promotion_success": self.production_promotion_success,
            "started_at": self.started_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "final_performance_metrics": self.final_performance_metrics,
            "constitutional_hash": self.constitutional_hash,
            "constitutional_compliance_verified": self.constitutional_compliance_verified,
        }


class MLOpsManager:
    """
    Main MLOps orchestration manager.

    Provides unified interface for model versioning, artifact storage,
    Git integration, and deployment pipelines with constitutional compliance.
    """

    def __init__(self, config: MLOpsConfig | None = None):
        self.config = config or MLOpsConfig()

        # Ensure storage directories exist
        self._create_storage_directories()

        # Initialize components
        self.version_manager = ModelVersionManager(
            storage_path=self.config.model_versions_path,
            constitutional_hash=self.config.constitutional_hash,
        )

        self.git_tracker = GitTracker(
            repo_path=self.config.git_repo_path,
            constitutional_hash=self.config.constitutional_hash,
        )

        self.artifact_manager = ArtifactManager(
            storage_root=self.config.artifacts_path,
            enable_compression=self.config.enable_compression,
            constitutional_hash=self.config.constitutional_hash,
        )

        self.deployment_pipeline = DeploymentPipeline(
            storage_path=self.config.deployments_path,
            constitutional_hash=self.config.constitutional_hash,
        )

        logger.info("MLOpsManager initialized with constitutional hash verification")
        logger.info(f"Storage root: {self.config.storage_root}")
        logger.info(f"Constitutional hash: {self.config.constitutional_hash}")

    def _create_storage_directories(self):
        """Create necessary storage directories."""
        directories = [
            self.config.storage_root,
            self.config.model_versions_path,
            self.config.artifacts_path,
            self.config.deployments_path,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def create_model_version(
        self,
        model_name: str,
        model_path: str | Path,
        config_path: str | Path,
        performance_metrics: dict[str, float],
        version_policy: VersionPolicy = VersionPolicy.PATCH,
        parent_version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MLOpsModelVersion:
        """
        Create a new model version with full MLOps integration.

        Args:
            model_name: Name of the model
            model_path: Path to model file
            config_path: Path to configuration file
            performance_metrics: Model performance metrics
            version_policy: Version increment policy
            parent_version: Parent version for lineage
            metadata: Additional metadata

        Returns:
            MLOpsModelVersion: Created model version
        """

        logger.info(f"Creating model version for {model_name}")

        # Validate constitutional compliance
        constitutional_compliance = performance_metrics.get(
            "constitutional_compliance", 0.0
        )
        if (
            constitutional_compliance
            < self.config.performance_targets["constitutional_compliance"]
        ):
            logger.warning(
                f"Constitutional compliance {constitutional_compliance:.3f} below target "
                f"{self.config.performance_targets['constitutional_compliance']:.3f}"
            )

        # Get current Git commit information
        current_commit = self.git_tracker.git.get_current_commit()

        # Validate deployment readiness
        deployment_readiness = self.git_tracker.validate_deployment_readiness()
        if not deployment_readiness["is_ready"]:
            logger.warning(
                f"Deployment readiness issues: {deployment_readiness['issues']}"
            )

        # Create model version
        model_version = self.version_manager.create_version(
            model_name=model_name,
            model_artifact_path=str(model_path),
            config_artifact_path=str(config_path),
            performance_metrics=performance_metrics,
            git_commit_hash=current_commit.hash,
            git_branch=current_commit.branch,
            version_policy=version_policy,
            parent_version=parent_version,
            metadata=metadata,
        )

        # Store artifacts
        artifact_ids = self.artifact_manager.store_model_artifacts(
            model_name=model_name,
            version=str(model_version.version),
            model_path=model_path,
            config_path=config_path,
            metrics=performance_metrics,
            parent_model_id=parent_version,
        )

        # Create Git tag if enabled
        git_tag = None
        if self.config.auto_git_tagging:
            try:
                tag_info = self.git_tracker.track_model_version(
                    model_name=model_name,
                    version=str(model_version.version),
                    performance_metrics=performance_metrics,
                )
                git_tag = tag_info.name
                model_version.git_tag = git_tag
            except Exception as e:
                logger.warning(f"Failed to create Git tag: {e}")

        logger.info(f"Created model version {model_version.version} for {model_name}")
        logger.info(f"  Artifact IDs: {artifact_ids}")
        logger.info(f"  Git tag: {git_tag}")
        logger.info(f"  Constitutional compliance: {constitutional_compliance:.3f}")

        return model_version

    def deploy_model(
        self,
        model_name: str,
        model_version: str,
        skip_staging: bool = False,
        custom_validation_config: dict[str, Any] | None = None,
        custom_promotion_config: dict[str, Any] | None = None,
    ) -> DeploymentResult:
        """
        Deploy a model through the complete MLOps pipeline.

        Args:
            model_name: Name of the model to deploy
            model_version: Version of the model to deploy
            skip_staging: Skip staging validation (not recommended)
            custom_validation_config: Custom validation configuration
            custom_promotion_config: Custom promotion configuration

        Returns:
            DeploymentResult: Complete deployment result
        """

        logger.info(f"Starting deployment for {model_name} v{model_version}")

        # Get model version
        model_version_obj = self.version_manager.get_version_by_model_and_version(
            model_name, model_version
        )
        if not model_version_obj:
            raise MLOpsError(f"Model version not found: {model_name} v{model_version}")

        # Validate constitutional compliance
        if (
            not model_version_obj.constitutional_compliance_score
            >= self.config.performance_targets["constitutional_compliance"]
        ):
            raise MLOpsError(
                f"Model does not meet constitutional compliance requirements: "
                f"{model_version_obj.constitutional_compliance_score:.3f}"
            )

        started_at = datetime.now(timezone.utc)

        # Create deployment record
        deployment_config = {
            "model_name": model_name,
            "model_version": model_version,
            "skip_staging": skip_staging,
            "constitutional_hash": self.config.constitutional_hash,
        }

        deployment_record = self.deployment_pipeline.create_deployment(
            model_name=model_name,
            model_version=model_version,
            deployment_config=deployment_config,
        )

        deployment_result = DeploymentResult(
            deployment_id=deployment_record.deployment_id,
            model_version=model_version_obj,
            artifact_ids={},  # Will be populated
            git_tag=model_version_obj.git_tag or "",
            deployment_status=DeploymentStatus.PENDING,
            staging_validation_passed=False,
            production_promotion_success=False,
            started_at=started_at,
            constitutional_hash=self.config.constitutional_hash,
        )

        try:
            # Get artifact IDs for the model
            artifacts = self.artifact_manager.storage.list_artifacts(name=model_name)
            model_artifacts = [a for a in artifacts if a.version == model_version]

            if model_artifacts:
                deployment_result.artifact_ids = {
                    a.artifact_type: a.artifact_id for a in model_artifacts
                }

            # Run staging validation (unless skipped)
            if not skip_staging:
                validation_config = (
                    custom_validation_config or self.config.staging_validation_config
                )

                staging_success = self.deployment_pipeline.run_staging_validation(
                    deployment_record.deployment_id, validation_config
                )

                deployment_result.staging_validation_passed = staging_success
                deployment_result.deployment_status = (
                    DeploymentStatus.STAGING
                    if staging_success
                    else DeploymentStatus.FAILED
                )

                if not staging_success:
                    logger.error(
                        f"Staging validation failed for {deployment_record.deployment_id}"
                    )
                    deployment_result.completed_at = datetime.now(timezone.utc)
                    return deployment_result
            else:
                deployment_result.staging_validation_passed = True
                deployment_result.deployment_status = DeploymentStatus.STAGING

            # Promote to production
            promotion_config = (
                custom_promotion_config or self.config.production_promotion_config
            )

            promotion_success = self.deployment_pipeline.promote_to_production(
                deployment_record.deployment_id, promotion_config
            )

            deployment_result.production_promotion_success = promotion_success
            deployment_result.deployment_status = (
                DeploymentStatus.DEPLOYED
                if promotion_success
                else DeploymentStatus.FAILED
            )

            if promotion_success:
                # Update model version as production
                self.version_manager.promote_to_production(model_version)
                deployment_result.constitutional_compliance_verified = True

                logger.info(
                    f"Successfully deployed {model_name} v{model_version} to production"
                )
            else:
                logger.error(
                    f"Production promotion failed for {deployment_record.deployment_id}"
                )

            deployment_result.completed_at = datetime.now(timezone.utc)
            deployment_result.final_performance_metrics = (
                model_version_obj.performance_metrics
            )

            return deployment_result

        except Exception as e:
            deployment_result.deployment_status = DeploymentStatus.FAILED
            deployment_result.completed_at = datetime.now(timezone.utc)

            logger.error(f"Deployment failed for {model_name} v{model_version}: {e}")
            raise MLOpsError(f"Deployment failed: {e}")

    def rollback_model(self, model_name: str, rollback_reason: str) -> bool:
        """
        Rollback model to previous production version.

        Args:
            model_name: Name of the model to rollback
            rollback_reason: Reason for rollback

        Returns:
            bool: Rollback success status
        """

        logger.info(f"Rolling back model {model_name}")
        logger.info(f"Rollback reason: {rollback_reason}")

        try:
            # Rollback in version manager
            previous_version = self.version_manager.rollback_production(model_name)

            if not previous_version:
                logger.error(f"No previous version found for rollback of {model_name}")
                return False

            # Find current deployment to rollback
            deployments = self.deployment_pipeline.list_deployments(
                status=DeploymentStatus.DEPLOYED, model_name=model_name
            )

            if deployments:
                current_deployment = deployments[0]  # Most recent
                rollback_success = self.deployment_pipeline.rollback_deployment(
                    current_deployment.deployment_id, rollback_reason
                )

                if rollback_success:
                    logger.info(
                        f"Successfully rolled back {model_name} to version {previous_version.version}"
                    )
                    return True
                logger.error(f"Failed to rollback deployment for {model_name}")
                return False
            logger.warning(f"No active deployment found for {model_name}")
            return True  # Version rollback succeeded even if no deployment found

        except Exception as e:
            logger.error(f"Rollback failed for {model_name}: {e}")
            return False

    def get_model_status(self, model_name: str) -> dict[str, Any]:
        """Get comprehensive status for a model."""

        # Get latest version
        latest_version = self.version_manager.get_latest_version(model_name)
        production_version = self.version_manager.get_production_version(model_name)

        # Get recent deployments
        recent_deployments = self.deployment_pipeline.list_deployments(
            model_name=model_name
        )[
            :5
        ]  # Last 5 deployments

        # Get artifacts
        artifacts = self.artifact_manager.storage.list_artifacts(name=model_name)

        # Get Git version history
        git_history = self.git_tracker.get_model_version_history(model_name)

        return {
            "model_name": model_name,
            "latest_version": latest_version.to_dict() if latest_version else None,
            "production_version": (
                production_version.to_dict() if production_version else None
            ),
            "recent_deployments": [d.to_dict() for d in recent_deployments],
            "artifact_count": len(artifacts),
            "git_tags": len(git_history),
            "constitutional_hash": self.config.constitutional_hash,
            "constitutional_hash_verified": self.config.constitutional_hash
            == "cdd01ef066bc6cf2",
            "performance_targets": self.config.performance_targets,
        }

    def get_mlops_dashboard(self) -> dict[str, Any]:
        """Get comprehensive MLOps dashboard data."""

        # Get statistics from all components
        version_stats = {
            "total_versions": len(self.version_manager.versions),
            "production_versions": len(
                [v for v in self.version_manager.versions.values() if v.is_production]
            ),
        }

        artifact_stats = self.artifact_manager.storage.get_storage_stats()
        pipeline_stats = self.deployment_pipeline.get_pipeline_stats()

        # Get recent activity
        recent_versions = sorted(
            self.version_manager.versions.values(),
            key=lambda v: v.created_at,
            reverse=True,
        )[:10]

        recent_deployments = self.deployment_pipeline.list_deployments()[:10]

        return {
            "mlops_overview": {
                "constitutional_hash": self.config.constitutional_hash,
                "constitutional_hash_verified": self.config.constitutional_hash
                == "cdd01ef066bc6cf2",
                "performance_targets": self.config.performance_targets,
                "storage_root": self.config.storage_root,
            },
            "version_statistics": version_stats,
            "artifact_statistics": artifact_stats,
            "pipeline_statistics": pipeline_stats,
            "recent_versions": [v.to_dict() for v in recent_versions],
            "recent_deployments": [d.to_dict() for d in recent_deployments],
            "system_health": {
                "git_integration": True,
                "artifact_storage": True,
                "deployment_pipeline": True,
                "constitutional_compliance": True,
            },
        }
