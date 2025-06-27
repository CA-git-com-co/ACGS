"""
Artifact Storage and Lineage Tracking

Provides comprehensive artifact storage, versioning, and lineage tracking
for ML models, configurations, and related artifacts in the ACGS-PGP system.

This module ensures full traceability from data to deployment with
constitutional hash integrity verification.
"""

import logging
import json
import hashlib
import shutil
import gzip
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass


@dataclass
class ArtifactMetadata:
    """Metadata for stored artifacts."""
    
    artifact_id: str
    artifact_type: str  # 'model', 'config', 'data', 'metrics'
    name: str
    version: str
    
    # Storage information
    storage_path: str
    file_size_bytes: int
    checksum: str
    compression: bool = False
    
    # Lineage information
    parent_artifacts: List[str] = field(default_factory=list)
    child_artifacts: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    accessed_at: Optional[datetime] = None
    
    # Constitutional compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = asdict(self)
        
        # Convert datetime objects
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.accessed_at:
            data['accessed_at'] = self.accessed_at.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactMetadata":
        """Create from dictionary representation."""
        # Parse datetime strings
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        if 'accessed_at' in data and isinstance(data['accessed_at'], str):
            data['accessed_at'] = datetime.fromisoformat(data['accessed_at'])
        
        return cls(**data)


class ArtifactStorage:
    """
    Artifact storage system with versioning and lineage tracking.
    
    Provides secure storage for ML artifacts with compression,
    checksums, and full lineage tracking capabilities.
    """
    
    def __init__(self, storage_root: str = "./artifacts",
                 enable_compression: bool = True,
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.storage_root = Path(storage_root)
        self.enable_compression = enable_compression
        self.constitutional_hash = constitutional_hash
        
        # Create storage directories
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.storage_root / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Load existing metadata
        self.artifacts: Dict[str, ArtifactMetadata] = {}
        self._load_metadata()
        
        logger.info(f"ArtifactStorage initialized at {storage_root}")
    
    def _load_metadata(self):
        """Load existing artifact metadata."""
        metadata_file = self.metadata_dir / "artifacts.json"
        
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata_data = json.load(f)
                
                for artifact_id, artifact_data in metadata_data.items():
                    self.artifacts[artifact_id] = ArtifactMetadata.from_dict(artifact_data)
                
                logger.info(f"Loaded {len(self.artifacts)} artifact metadata entries")
            
            except Exception as e:
                logger.error(f"Failed to load artifact metadata: {e}")
    
    def _save_metadata(self):
        """Save artifact metadata to storage."""
        metadata_file = self.metadata_dir / "artifacts.json"
        
        try:
            metadata_data = {
                artifact_id: artifact.to_dict()
                for artifact_id, artifact in self.artifacts.items()
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata_data, f, indent=2, default=str)
            
            logger.debug("Artifact metadata saved")
        
        except Exception as e:
            logger.error(f"Failed to save artifact metadata: {e}")
            raise StorageError(f"Failed to save metadata: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file."""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def _compress_file(self, source_path: Path, target_path: Path):
        """Compress file using gzip."""
        with open(source_path, 'rb') as f_in:
            with gzip.open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _decompress_file(self, source_path: Path, target_path: Path):
        """Decompress gzip file."""
        with gzip.open(source_path, 'rb') as f_in:
            with open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def store_artifact(self, artifact_type: str, name: str, version: str,
                      source_path: Union[str, Path], 
                      parent_artifacts: Optional[List[str]] = None,
                      dependencies: Optional[Dict[str, str]] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> ArtifactMetadata:
        """
        Store an artifact with metadata and lineage tracking.
        
        Args:
            artifact_type: Type of artifact ('model', 'config', 'data', 'metrics')
            name: Artifact name
            version: Artifact version
            source_path: Path to source file/directory
            parent_artifacts: List of parent artifact IDs
            dependencies: Dictionary of dependencies
            metadata: Additional metadata
        
        Returns:
            ArtifactMetadata: Metadata for stored artifact
        """
        
        source_path = Path(source_path)
        
        if not source_path.exists():
            raise StorageError(f"Source path does not exist: {source_path}")
        
        # Generate artifact ID
        artifact_id = f"{artifact_type}_{name}_{version}_{int(datetime.now().timestamp())}"
        
        logger.info(f"Storing artifact: {artifact_id}")
        
        # Create storage directory for artifact type
        type_dir = self.storage_root / artifact_type
        type_dir.mkdir(exist_ok=True)
        
        # Determine target path
        if source_path.is_file():
            target_filename = f"{name}_{version}"
            if self.enable_compression:
                target_filename += ".gz"
            target_path = type_dir / target_filename
        else:
            # For directories, create a compressed archive
            target_filename = f"{name}_{version}.tar.gz"
            target_path = type_dir / target_filename
        
        try:
            # Store the artifact
            if source_path.is_file():
                if self.enable_compression:
                    self._compress_file(source_path, target_path)
                else:
                    shutil.copy2(source_path, target_path)
            else:
                # Create compressed archive for directories
                shutil.make_archive(
                    str(target_path.with_suffix('')), 'gztar', source_path
                )
            
            # Calculate checksum
            checksum = self._calculate_checksum(target_path)
            
            # Get file size
            file_size = target_path.stat().st_size
            
            # Create metadata
            artifact_metadata = ArtifactMetadata(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                name=name,
                version=version,
                storage_path=str(target_path),
                file_size_bytes=file_size,
                checksum=checksum,
                compression=self.enable_compression,
                parent_artifacts=parent_artifacts or [],
                dependencies=dependencies or {},
                constitutional_hash=self.constitutional_hash,
                metadata=metadata or {}
            )
            
            # Store metadata
            self.artifacts[artifact_id] = artifact_metadata
            self._save_metadata()
            
            # Update parent-child relationships
            if parent_artifacts:
                for parent_id in parent_artifacts:
                    if parent_id in self.artifacts:
                        self.artifacts[parent_id].child_artifacts.append(artifact_id)
            
            logger.info(f"Stored artifact {artifact_id} ({file_size} bytes)")
            logger.info(f"  Storage path: {target_path}")
            logger.info(f"  Checksum: {checksum[:16]}...")
            
            return artifact_metadata
        
        except Exception as e:
            # Clean up on failure
            if target_path.exists():
                target_path.unlink()
            raise StorageError(f"Failed to store artifact: {e}")
    
    def retrieve_artifact(self, artifact_id: str, 
                         target_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Retrieve an artifact from storage.
        
        Args:
            artifact_id: ID of artifact to retrieve
            target_path: Optional target path for extraction
        
        Returns:
            Path: Path to retrieved artifact
        """
        
        if artifact_id not in self.artifacts:
            raise StorageError(f"Artifact not found: {artifact_id}")
        
        artifact = self.artifacts[artifact_id]
        storage_path = Path(artifact.storage_path)
        
        if not storage_path.exists():
            raise StorageError(f"Artifact file not found: {storage_path}")
        
        logger.info(f"Retrieving artifact: {artifact_id}")
        
        # Verify checksum
        current_checksum = self._calculate_checksum(storage_path)
        if current_checksum != artifact.checksum:
            raise StorageError(f"Checksum mismatch for artifact {artifact_id}")
        
        # Update access time
        artifact.accessed_at = datetime.now(timezone.utc)
        self._save_metadata()
        
        # If no target path specified, return storage path
        if target_path is None:
            if artifact.compression:
                # Create temporary decompressed file
                temp_path = storage_path.parent / f"temp_{artifact.name}_{artifact.version}"
                self._decompress_file(storage_path, temp_path)
                return temp_path
            else:
                return storage_path
        
        target_path = Path(target_path)
        
        # Extract/copy to target path
        if artifact.compression:
            if storage_path.suffix == '.gz' and not storage_path.name.endswith('.tar.gz'):
                # Single compressed file
                self._decompress_file(storage_path, target_path)
            else:
                # Compressed archive
                shutil.unpack_archive(storage_path, target_path)
        else:
            if storage_path.is_file():
                shutil.copy2(storage_path, target_path)
            else:
                shutil.copytree(storage_path, target_path)
        
        logger.info(f"Retrieved artifact {artifact_id} to {target_path}")
        return target_path
    
    def get_artifact_metadata(self, artifact_id: str) -> Optional[ArtifactMetadata]:
        """Get metadata for a specific artifact."""
        return self.artifacts.get(artifact_id)
    
    def list_artifacts(self, artifact_type: Optional[str] = None,
                      name: Optional[str] = None) -> List[ArtifactMetadata]:
        """List artifacts with optional filtering."""
        artifacts = list(self.artifacts.values())
        
        if artifact_type:
            artifacts = [a for a in artifacts if a.artifact_type == artifact_type]
        
        if name:
            artifacts = [a for a in artifacts if a.name == name]
        
        return sorted(artifacts, key=lambda a: a.created_at, reverse=True)
    
    def delete_artifact(self, artifact_id: str, force: bool = False) -> bool:
        """
        Delete an artifact from storage.
        
        Args:
            artifact_id: ID of artifact to delete
            force: Force deletion even if artifact has children
        
        Returns:
            bool: Success status
        """
        
        if artifact_id not in self.artifacts:
            raise StorageError(f"Artifact not found: {artifact_id}")
        
        artifact = self.artifacts[artifact_id]
        
        # Check for child artifacts
        if artifact.child_artifacts and not force:
            raise StorageError(
                f"Artifact {artifact_id} has child artifacts. Use force=True to delete.")
        
        logger.info(f"Deleting artifact: {artifact_id}")
        
        # Delete file
        storage_path = Path(artifact.storage_path)
        if storage_path.exists():
            storage_path.unlink()
        
        # Remove from metadata
        del self.artifacts[artifact_id]
        
        # Update parent-child relationships
        for parent_id in artifact.parent_artifacts:
            if parent_id in self.artifacts:
                parent = self.artifacts[parent_id]
                if artifact_id in parent.child_artifacts:
                    parent.child_artifacts.remove(artifact_id)
        
        self._save_metadata()
        
        logger.info(f"Deleted artifact {artifact_id}")
        return True
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        total_size = sum(a.file_size_bytes for a in self.artifacts.values())
        
        type_stats = {}
        for artifact in self.artifacts.values():
            if artifact.artifact_type not in type_stats:
                type_stats[artifact.artifact_type] = {'count': 0, 'size': 0}
            type_stats[artifact.artifact_type]['count'] += 1
            type_stats[artifact.artifact_type]['size'] += artifact.file_size_bytes
        
        return {
            'total_artifacts': len(self.artifacts),
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024),
            'type_statistics': type_stats,
            'storage_root': str(self.storage_root),
            'compression_enabled': self.enable_compression,
            'constitutional_hash': self.constitutional_hash,
            'constitutional_hash_verified': self.constitutional_hash == "cdd01ef066bc6cf2"
        }


class LineageTracker:
    """
    Tracks lineage relationships between artifacts.
    
    Provides functionality to trace artifact dependencies
    and relationships for full ML pipeline traceability.
    """
    
    def __init__(self, artifact_storage: ArtifactStorage):
        self.storage = artifact_storage
        
        logger.info("LineageTracker initialized")
    
    def trace_lineage(self, artifact_id: str, direction: str = "both") -> Dict[str, Any]:
        """
        Trace lineage for an artifact.
        
        Args:
            artifact_id: ID of artifact to trace
            direction: 'upstream', 'downstream', or 'both'
        
        Returns:
            Dict with lineage information
        """
        
        if artifact_id not in self.storage.artifacts:
            raise StorageError(f"Artifact not found: {artifact_id}")
        
        artifact = self.storage.artifacts[artifact_id]
        
        lineage = {
            'artifact_id': artifact_id,
            'artifact_info': artifact.to_dict(),
            'upstream': [],
            'downstream': []
        }
        
        # Trace upstream (parents)
        if direction in ['upstream', 'both']:
            lineage['upstream'] = self._trace_upstream(artifact_id, set())
        
        # Trace downstream (children)
        if direction in ['downstream', 'both']:
            lineage['downstream'] = self._trace_downstream(artifact_id, set())
        
        return lineage
    
    def _trace_upstream(self, artifact_id: str, visited: set) -> List[Dict[str, Any]]:
        """Recursively trace upstream dependencies."""
        if artifact_id in visited:
            return []
        
        visited.add(artifact_id)
        
        if artifact_id not in self.storage.artifacts:
            return []
        
        artifact = self.storage.artifacts[artifact_id]
        upstream = []
        
        for parent_id in artifact.parent_artifacts:
            if parent_id in self.storage.artifacts:
                parent_artifact = self.storage.artifacts[parent_id]
                upstream.append({
                    'artifact_id': parent_id,
                    'artifact_info': parent_artifact.to_dict(),
                    'upstream': self._trace_upstream(parent_id, visited.copy())
                })
        
        return upstream
    
    def _trace_downstream(self, artifact_id: str, visited: set) -> List[Dict[str, Any]]:
        """Recursively trace downstream dependencies."""
        if artifact_id in visited:
            return []
        
        visited.add(artifact_id)
        
        if artifact_id not in self.storage.artifacts:
            return []
        
        artifact = self.storage.artifacts[artifact_id]
        downstream = []
        
        for child_id in artifact.child_artifacts:
            if child_id in self.storage.artifacts:
                child_artifact = self.storage.artifacts[child_id]
                downstream.append({
                    'artifact_id': child_id,
                    'artifact_info': child_artifact.to_dict(),
                    'downstream': self._trace_downstream(child_id, visited.copy())
                })
        
        return downstream
    
    def validate_lineage_integrity(self) -> Dict[str, Any]:
        """Validate integrity of lineage relationships."""
        issues = []
        
        for artifact_id, artifact in self.storage.artifacts.items():
            # Check parent relationships
            for parent_id in artifact.parent_artifacts:
                if parent_id not in self.storage.artifacts:
                    issues.append(f"Missing parent artifact {parent_id} for {artifact_id}")
                else:
                    parent = self.storage.artifacts[parent_id]
                    if artifact_id not in parent.child_artifacts:
                        issues.append(f"Broken parent-child link: {parent_id} -> {artifact_id}")
            
            # Check child relationships
            for child_id in artifact.child_artifacts:
                if child_id not in self.storage.artifacts:
                    issues.append(f"Missing child artifact {child_id} for {artifact_id}")
                else:
                    child = self.storage.artifacts[child_id]
                    if artifact_id not in child.parent_artifacts:
                        issues.append(f"Broken child-parent link: {artifact_id} -> {child_id}")
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'total_artifacts': len(self.storage.artifacts),
            'validation_timestamp': datetime.now(timezone.utc).isoformat()
        }


class ArtifactManager:
    """
    High-level artifact management interface.
    
    Combines storage and lineage tracking for simplified
    artifact management in MLOps workflows.
    """
    
    def __init__(self, storage_root: str = "./artifacts",
                 enable_compression: bool = True,
                 constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.storage = ArtifactStorage(storage_root, enable_compression, constitutional_hash)
        self.lineage = LineageTracker(self.storage)
        self.constitutional_hash = constitutional_hash
        
        logger.info("ArtifactManager initialized")
    
    def store_model_artifacts(self, model_name: str, version: str,
                             model_path: Union[str, Path],
                             config_path: Union[str, Path],
                             metrics: Dict[str, float],
                             parent_model_id: Optional[str] = None) -> Dict[str, str]:
        """
        Store complete set of model artifacts.
        
        Args:
            model_name: Name of the model
            version: Model version
            model_path: Path to model file
            config_path: Path to configuration file
            metrics: Performance metrics
            parent_model_id: ID of parent model (for lineage)
        
        Returns:
            Dict with artifact IDs
        """
        
        logger.info(f"Storing model artifacts for {model_name} v{version}")
        
        parent_artifacts = [parent_model_id] if parent_model_id else []
        
        # Store model artifact
        model_artifact = self.storage.store_artifact(
            artifact_type="model",
            name=model_name,
            version=version,
            source_path=model_path,
            parent_artifacts=parent_artifacts,
            metadata={'type': 'trained_model'}
        )
        
        # Store configuration artifact
        config_artifact = self.storage.store_artifact(
            artifact_type="config",
            name=f"{model_name}_config",
            version=version,
            source_path=config_path,
            parent_artifacts=[model_artifact.artifact_id],
            metadata={'type': 'model_config'}
        )
        
        # Store metrics artifact
        metrics_artifact = self.storage.store_artifact(
            artifact_type="metrics",
            name=f"{model_name}_metrics",
            version=version,
            source_path=self._create_metrics_file(metrics, model_name, version),
            parent_artifacts=[model_artifact.artifact_id],
            metadata={'type': 'performance_metrics', 'metrics': metrics}
        )
        
        artifact_ids = {
            'model': model_artifact.artifact_id,
            'config': config_artifact.artifact_id,
            'metrics': metrics_artifact.artifact_id
        }
        
        logger.info(f"Stored {len(artifact_ids)} artifacts for {model_name} v{version}")
        
        return artifact_ids
    
    def _create_metrics_file(self, metrics: Dict[str, float], 
                           model_name: str, version: str) -> Path:
        """Create temporary metrics file."""
        metrics_data = {
            'model_name': model_name,
            'version': version,
            'metrics': metrics,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'constitutional_hash': self.constitutional_hash
        }
        
        temp_file = Path(f"/tmp/{model_name}_{version}_metrics.json")
        with open(temp_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        return temp_file
    
    def get_model_lineage(self, model_artifact_id: str) -> Dict[str, Any]:
        """Get complete lineage for a model."""
        return self.lineage.trace_lineage(model_artifact_id)
    
    def cleanup_old_artifacts(self, days_old: int = 90) -> int:
        """Clean up artifacts older than specified days."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        deleted_count = 0
        for artifact_id, artifact in list(self.storage.artifacts.items()):
            if artifact.created_at < cutoff_date and not artifact.child_artifacts:
                try:
                    self.storage.delete_artifact(artifact_id)
                    deleted_count += 1
                except StorageError as e:
                    logger.warning(f"Failed to delete old artifact {artifact_id}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} old artifacts")
        return deleted_count
