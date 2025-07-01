"""
ACGS-1 API Versioning Tools

Comprehensive toolset for API lifecycle management including:
- API diff analysis
- Automated migration scripts
- Version deployment tools
- Rollback procedures
- Health checks and validation
"""

from .api_diff import APIDiffAnalyzer, DiffReport, ChangeType
from .migration_generator import MigrationGenerator, MigrationScript
from .deployment_manager import DeploymentManager, DeploymentStrategy
from .health_checker import VersionHealthChecker, HealthStatus
from .rollback_manager import RollbackManager, RollbackPlan

__all__ = [
    "APIDiffAnalyzer",
    "DiffReport",
    "ChangeType",
    "MigrationGenerator",
    "MigrationScript",
    "DeploymentManager",
    "DeploymentStrategy",
    "VersionHealthChecker",
    "HealthStatus",
    "RollbackManager",
    "RollbackPlan",
]

__version__ = "1.0.0"
