"""
MLOps Model Versioning System

Enhanced model versioning with semantic versioning (MAJOR.MINOR.PATCH),
Git integration, and constitutional hash integrity for ACGS-PGP system.

This module extends the existing ModelVersion class with comprehensive
versioning capabilities, automated version management, and integration
with Git for full traceability.
"""

import logging
import json
import hashlib
from datetime import datetime, timezone
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

logger = logging.getLogger(__name__)


class VersionPolicy(str, Enum):
    """Version increment policies following semantic versioning."""
    
    MAJOR = "major"  # Breaking changes, incompatible API changes
    MINOR = "minor"  # New features, backward compatible
    PATCH = "patch"  # Bug fixes, backward compatible


class VersioningError(Exception):
    """Raised when versioning operations fail."""
    pass


@dataclass
class SemanticVersion:
    """
    Semantic version representation following SemVer specification.
    
    Format: MAJOR.MINOR.PATCH[-prerelease][+build]
    """
    
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None
    
    def __post_init__(self):
        """Validate version components."""
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise VersioningError("Version components must be non-negative")
    
    @classmethod
    def from_string(cls, version_str: str) -> "SemanticVersion":
        """Parse version string into SemanticVersion object."""
        import re
        
        # Remove 'v' prefix if present
        version_str = version_str.lstrip("v")
        
        # SemVer regex pattern
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
        match = re.match(pattern, version_str)
        
        if not match:
            raise VersioningError(f"Invalid semantic version format: {version_str}")
        
        major, minor, patch, prerelease, build = match.groups()
        
        return cls(
            major=int(major),
            minor=int(minor),
            patch=int(patch),
            prerelease=prerelease,
            build=build
        )
    
    def __str__(self) -> str:
        """String representation of semantic version."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        
        if self.prerelease:
            version += f"-{self.prerelease}"
        
        if self.build:
            version += f"+{self.build}"
        
        return version
    
    def __lt__(self, other: "SemanticVersion") -> bool:
        """Compare versions for ordering."""
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        
        # Compare major.minor.patch
        self_tuple = (self.major, self.minor, self.patch)
        other_tuple = (other.major, other.minor, other.patch)
        
        if self_tuple != other_tuple:
            return self_tuple < other_tuple
        
        # Handle prerelease comparison
        if self.prerelease is None and other.prerelease is None:
            return False
        elif self.prerelease is None:
            return False  # Release version > prerelease
        elif other.prerelease is None:
            return True   # Prerelease < release version
        else:
            return self.prerelease < other.prerelease
    
    def bump(self, policy: VersionPolicy, prerelease: Optional[str] = None) -> "SemanticVersion":
        """Create new version with specified bump policy."""
        if policy == VersionPolicy.MAJOR:
            return SemanticVersion(
                major=self.major + 1,
                minor=0,
                patch=0,
                prerelease=prerelease
            )
        elif policy == VersionPolicy.MINOR:
            return SemanticVersion(
                major=self.major,
                minor=self.minor + 1,
                patch=0,
                prerelease=prerelease
            )
        else:  # PATCH
            return SemanticVersion(
                major=self.major,
                minor=self.minor,
                patch=self.patch + 1,
                prerelease=prerelease
            )


@dataclass
class MLOpsModelVersion:
    """
    Enhanced model version with MLOps capabilities.
    
    Extends the basic ModelVersion with semantic versioning,
    Git integration, artifact tracking, and lineage information.
    """
    
    # Core version information
    version: SemanticVersion
    model_id: str
    model_name: str
    
    # Model artifacts and metadata
    model_artifact_path: str
    config_artifact_path: str
    performance_metrics: Dict[str, float]
    
    # Git integration
    git_commit_hash: str
    git_branch: str
    git_tag: Optional[str] = None
    
    # Timestamps and tracking
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    deployed_at: Optional[datetime] = None
    
    # Constitutional and compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"
    constitutional_compliance_score: float = 0.0
    
    # Lineage and dependencies
    parent_version: Optional[str] = None
    training_data_hash: Optional[str] = None
    dependencies: Dict[str, str] = field(default_factory=dict)
    
    # Status and metadata
    is_active: bool = False
    is_production: bool = False
    deployment_environment: str = "development"
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate model version after initialization."""
        if self.constitutional_hash != "cdd01ef066bc6cf2":
            raise VersioningError(f"Invalid constitutional hash: {self.constitutional_hash}")
        
        if not (0.0 <= self.constitutional_compliance_score <= 1.0):
            raise VersioningError("Constitutional compliance score must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model version to dictionary representation."""
        data = asdict(self)
        
        # Convert datetime objects to ISO format
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.deployed_at:
            data['deployed_at'] = self.deployed_at.isoformat()
        
        # Convert SemanticVersion to string
        data['version'] = str(self.version)
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MLOpsModelVersion":
        """Create model version from dictionary representation."""
        # Parse version string
        if isinstance(data['version'], str):
            data['version'] = SemanticVersion.from_string(data['version'])
        
        # Parse datetime strings
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'deployed_at' in data and isinstance(data['deployed_at'], str):
            data['deployed_at'] = datetime.fromisoformat(data['deployed_at'])
        
        return cls(**data)
    
    def calculate_model_hash(self) -> str:
        """Calculate hash of model artifacts for integrity verification."""
        hash_data = {
            'model_artifact_path': self.model_artifact_path,
            'config_artifact_path': self.config_artifact_path,
            'git_commit_hash': self.git_commit_hash,
            'constitutional_hash': self.constitutional_hash
        }
        
        hash_string = json.dumps(hash_data, sort_keys=True)
        return hashlib.sha256(hash_string.encode()).hexdigest()
    
    def is_compatible_with(self, other: "MLOpsModelVersion") -> bool:
        """Check if this version is compatible with another version."""
        # Same major version indicates compatibility
        return self.version.major == other.version.major
    
    def get_lineage_chain(self) -> List[str]:
        """Get the lineage chain of parent versions."""
        chain = [str(self.version)]
        
        if self.parent_version:
            chain.append(self.parent_version)
        
        return chain


class ModelVersionManager:
    """
    Manages model versions with semantic versioning and Git integration.
    
    Provides comprehensive version management including creation, tracking,
    promotion, and lifecycle management of ML models.
    """
    
    def __init__(self, storage_path: str = "./model_versions", 
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.storage_path = Path(storage_path)
        self.constitutional_hash = constitutional_hash
        self.versions: Dict[str, MLOpsModelVersion] = {}
        
        # Create storage directory
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing versions
        self._load_versions()
        
        logger.info(f"ModelVersionManager initialized with storage: {storage_path}")
    
    def _load_versions(self):
        """Load existing versions from storage."""
        versions_file = self.storage_path / "versions.json"
        
        if versions_file.exists():
            try:
                with open(versions_file, 'r') as f:
                    versions_data = json.load(f)
                
                for version_str, version_data in versions_data.items():
                    self.versions[version_str] = MLOpsModelVersion.from_dict(version_data)
                
                logger.info(f"Loaded {len(self.versions)} existing model versions")
            
            except Exception as e:
                logger.error(f"Failed to load existing versions: {e}")
    
    def _save_versions(self):
        """Save versions to storage."""
        versions_file = self.storage_path / "versions.json"

        try:
            versions_data = {
                version_str: version.to_dict()
                for version_str, version in self.versions.items()
            }

            with open(versions_file, 'w') as f:
                json.dump(versions_data, f, indent=2, default=str)

            logger.debug("Model versions saved to storage")

        except Exception as e:
            logger.error(f"Failed to save versions: {e}")
            raise VersioningError(f"Failed to save versions: {e}")

    def create_version(self, model_name: str, model_artifact_path: str,
                       config_artifact_path: str,
                       performance_metrics: Dict[str, float],
                       git_commit_hash: str, git_branch: str,
                       version_policy: VersionPolicy = VersionPolicy.PATCH,
                       parent_version: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None
                       ) -> MLOpsModelVersion:
        """
        Create a new model version with semantic versioning.

        Args:
            model_name: Name of the model
            model_artifact_path: Path to model artifacts
            config_artifact_path: Path to configuration artifacts
            performance_metrics: Model performance metrics
            git_commit_hash: Git commit hash for traceability
            git_branch: Git branch name
            version_policy: Version increment policy
            parent_version: Parent version for lineage tracking
            metadata: Additional metadata

        Returns:
            MLOpsModelVersion: Created model version
        """

        logger.info(f"Creating new model version for {model_name}")

        # Determine next version number
        latest_version = self.get_latest_version(model_name)

        if latest_version:
            new_semantic_version = latest_version.version.bump(version_policy)
        else:
            new_semantic_version = SemanticVersion(1, 0, 0)

        # Generate model ID
        model_id = f"{model_name}_{new_semantic_version}_{git_commit_hash[:8]}"

        # Validate constitutional compliance
        constitutional_compliance = performance_metrics.get(
            'constitutional_compliance', 0.0)
        if constitutional_compliance < 0.95:
            logger.warning(
                f"Constitutional compliance {constitutional_compliance:.3f} "
                f"below target 0.95")

        # Create model version
        model_version = MLOpsModelVersion(
            version=new_semantic_version,
            model_id=model_id,
            model_name=model_name,
            model_artifact_path=model_artifact_path,
            config_artifact_path=config_artifact_path,
            performance_metrics=performance_metrics,
            git_commit_hash=git_commit_hash,
            git_branch=git_branch,
            constitutional_hash=self.constitutional_hash,
            constitutional_compliance_score=constitutional_compliance,
            parent_version=parent_version,
            metadata=metadata or {}
        )

        # Store version
        version_key = str(new_semantic_version)
        self.versions[version_key] = model_version
        self._save_versions()

        logger.info(f"Created model version {version_key} for {model_name}")
        logger.info(f"  Model ID: {model_id}")
        logger.info(f"  Git commit: {git_commit_hash}")
        logger.info(
            f"  Constitutional compliance: {constitutional_compliance:.3f}")
        logger.debug(f"  Stored in versions dict with key: {version_key}")
        logger.debug(f"  Model name in version object: {model_version.model_name}")
        logger.debug(f"  Total versions stored: {len(self.versions)}")

        return model_version

    def get_version(self, version: Union[str, SemanticVersion]
                    ) -> Optional[MLOpsModelVersion]:
        """Get specific model version."""
        version_str = str(version)
        return self.versions.get(version_str)

    def get_version_by_model_and_version(self, model_name: str, version: Union[str, SemanticVersion]
                                       ) -> Optional[MLOpsModelVersion]:
        """Get specific model version by model name and version."""
        version_str = str(version)

        logger.debug(f"Looking for model: {model_name}, version: {version_str}")
        logger.debug(f"Available versions: {list(self.versions.keys())}")

        # First try direct lookup
        model_version = self.versions.get(version_str)
        if model_version and model_version.model_name == model_name:
            logger.debug(f"Found via direct lookup: {model_version.model_name} v{model_version.version}")
            return model_version

        # If not found, search through all versions
        for k, v in self.versions.items():
            logger.debug(f"Checking stored version: key={k}, model_name={v.model_name}, version={v.version}")
            if v.model_name == model_name and str(v.version) == version_str:
                logger.debug(f"Found via search: {v.model_name} v{v.version}")
                return v

        logger.debug(f"Version not found: {model_name} v{version_str}")
        return None

    def get_latest_version(self, model_name: Optional[str] = None
                           ) -> Optional[MLOpsModelVersion]:
        """Get latest version, optionally filtered by model name."""
        filtered_versions = self.versions.values()

        if model_name:
            filtered_versions = [v for v in filtered_versions
                                if v.model_name == model_name]

        if not filtered_versions:
            return None

        return max(filtered_versions, key=lambda v: v.version)

    def get_production_version(self, model_name: Optional[str] = None
                               ) -> Optional[MLOpsModelVersion]:
        """Get current production version."""
        filtered_versions = [v for v in self.versions.values()
                             if v.is_production]

        if model_name:
            filtered_versions = [v for v in filtered_versions
                                 if v.model_name == model_name]

        if not filtered_versions:
            return None

        return max(filtered_versions, key=lambda v: v.version)

    def promote_to_production(self, version: Union[str, SemanticVersion],
                              deployment_environment: str = "production"
                              ) -> bool:
        """
        Promote model version to production.

        Args:
            version: Version to promote
            deployment_environment: Target deployment environment

        Returns:
            bool: Success status
        """

        version_str = str(version)
        model_version = self.versions.get(version_str)

        if not model_version:
            raise VersioningError(f"Version {version_str} not found")

        logger.info(f"Promoting version {version_str} to production")

        # Demote current production version
        current_production = self.get_production_version(
            model_version.model_name)
        if current_production:
            current_production.is_production = False
            logger.info(
                f"Demoted version {current_production.version} "
                f"from production")

        # Promote new version
        model_version.is_production = True
        model_version.deployment_environment = deployment_environment
        model_version.deployed_at = datetime.now(timezone.utc)

        self._save_versions()

        logger.info(
            f"Successfully promoted version {version_str} to production")
        return True

    def rollback_production(self, model_name: str
                            ) -> Optional[MLOpsModelVersion]:
        """
        Rollback production to previous version.

        Args:
            model_name: Name of the model to rollback

        Returns:
            MLOpsModelVersion: Previous version that was promoted, or None
        """

        logger.info(f"Rolling back production for model {model_name}")

        # Get current production version
        current_production = self.get_production_version(model_name)
        if not current_production:
            logger.warning(f"No production version found for {model_name}")
            return None

        # Find previous version
        model_versions = [v for v in self.versions.values()
                          if v.model_name == model_name
                          and v != current_production]

        if not model_versions:
            logger.warning(
                f"No previous version found for rollback of {model_name}")
            return None

        previous_version = max(model_versions, key=lambda v: v.version)

        # Perform rollback
        current_production.is_production = False
        previous_version.is_production = True
        previous_version.deployed_at = datetime.now(timezone.utc)

        self._save_versions()

        logger.info(
            f"Rolled back {model_name} from {current_production.version} "
            f"to {previous_version.version}")
        return previous_version
