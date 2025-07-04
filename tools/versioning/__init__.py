"""
ACGS-1 API Versioning Tools

Comprehensive toolset for API lifecycle management including:
- API diff analysis
- Automated migration scripts
- Version deployment tools
- Rollback procedures
- Health checks and validation
"""

from .api_diff import APIDiffAnalyzer, ChangeType, DiffReport
from .deployment_manager import DeploymentManager, DeploymentStrategy
from .health_checker import HealthStatus, VersionHealthChecker
from .migration_generator import MigrationGenerator, MigrationScript
from .rollback_manager import RollbackManager, RollbackPlan

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = [
    "APIDiffAnalyzer",
    "ChangeType",
    "DeploymentManager",
    "DeploymentStrategy",
    "DiffReport",
    "HealthStatus",
    "MigrationGenerator",
    "MigrationScript",
    "RollbackManager",
    "RollbackPlan",
    "VersionHealthChecker",
]

__version__ = "1.0.0"
