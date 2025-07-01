"""
ACGS-PGP MLOps Framework

Comprehensive MLOps integration providing model versioning, Git integration,
artifact storage, and deployment pipeline management for the ACGS-PGP system.

This framework extends the existing production ML optimizer with enterprise-grade
MLOps capabilities while maintaining constitutional hash integrity and performance targets.

Key Components:
- Model Versioning: Semantic versioning (MAJOR.MINOR.PATCH) with Git integration
- Artifact Storage: Full lineage tracking and artifact management
- Deployment Pipeline: Staging validation and production promotion workflows
- Git Integration: Code/config tracking and automated tagging
- MLOps Manager: Orchestration and integration with ACGS-PGP services

Constitutional Hash: cdd01ef066bc6cf2
Performance Targets: Sub-2s response times, >95% constitutional compliance, 74% cost savings
"""

from .model_versioning import (
    MLOpsModelVersion,
    SemanticVersion,
    ModelVersionManager,
    VersioningError,
    VersionPolicy,
)

from .git_integration import GitIntegration, GitTracker, GitError, CommitInfo, TagInfo

from .artifact_storage import (
    ArtifactStorage,
    ArtifactManager,
    ArtifactMetadata,
    LineageTracker,
    StorageError,
)

from .deployment_pipeline import (
    DeploymentPipeline,
    StagingValidator,
    ProductionPromoter,
    DeploymentStatus,
    PipelineError,
)

from .mlops_manager import MLOpsManager, MLOpsConfig, MLOpsError, DeploymentResult

__version__ = "1.0.0"
__author__ = "ACGS-PGP Development Team"
__license__ = "MIT"

# Constitutional hash for integrity verification
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets
PERFORMANCE_TARGETS = {
    "response_time_ms": 2000,  # Sub-2s response times
    "constitutional_compliance": 0.95,  # >95% compliance
    "cost_savings": 0.74,  # 74% cost savings
    "availability": 0.999,  # 99.9% availability
    "model_accuracy": 0.90,  # >90% prediction accuracy
}

# MLOps configuration defaults
DEFAULT_MLOPS_CONFIG = {
    "versioning": {
        "strategy": "semantic",
        "auto_increment": True,
        "git_integration": True,
        "constitutional_hash_verification": True,
    },
    "artifact_storage": {
        "backend": "filesystem",
        "compression": True,
        "encryption": True,
        "retention_days": 90,
    },
    "deployment": {
        "staging_validation": True,
        "production_promotion": "manual",
        "rollback_enabled": True,
        "health_check_timeout": 300,
    },
    "monitoring": {
        "performance_tracking": True,
        "drift_detection": True,
        "alert_thresholds": {
            "accuracy_degradation": 0.05,
            "response_time_increase": 0.20,
            "constitutional_compliance_drop": 0.02,
        },
    },
}

__all__ = [
    # Model Versioning
    "MLOpsModelVersion",
    "SemanticVersion",
    "ModelVersionManager",
    "VersioningError",
    "VersionPolicy",
    # Git Integration
    "GitIntegration",
    "GitTracker",
    "GitError",
    "CommitInfo",
    "TagInfo",
    # Artifact Storage
    "ArtifactStorage",
    "ArtifactManager",
    "ArtifactMetadata",
    "LineageTracker",
    "StorageError",
    # Deployment Pipeline
    "DeploymentPipeline",
    "StagingValidator",
    "ProductionPromoter",
    "DeploymentStatus",
    "PipelineError",
    # MLOps Manager
    "MLOpsManager",
    "MLOpsConfig",
    "MLOpsError",
    "DeploymentResult",
    # Constants
    "CONSTITUTIONAL_HASH",
    "PERFORMANCE_TARGETS",
    "DEFAULT_MLOPS_CONFIG",
]
