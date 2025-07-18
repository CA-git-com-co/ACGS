#!/usr/bin/env python3
"""
ACGS-2 Functional Duplicate Consolidator
Constitutional Hash: cdd01ef066bc6cf2

Consolidates functional duplicates by creating shared base classes
and updating services to inherit from them.
"""

import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ACGSFunctionalDuplicateConsolidator:
    """
    Consolidates functional duplicates by creating shared base classes.
    """

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Services with duplicate database configurations
        self.services_with_db_config = [
            "services/core/evolutionary-computation/ec_service_standardized",
            "services/core/policy-governance/pgc_service_standardized", 
            "services/core/constitutional-ai/ac_service_standardized",
            "services/core/governance-synthesis/gs_service_standardized",
        ]
        
        self.consolidation_report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "services_updated": [],
            "shared_configs_created": [],
            "errors": []
        }

    def analyze_database_config_duplicates(self) -> Dict[str, List[str]]:
        """Analyze database configuration duplicates across services."""
        logger.info("🔍 Analyzing database configuration duplicates...")
        
        config_patterns = {}
        
        for service_path in self.services_with_db_config:
            config_file = self.project_root / service_path / "config.py"
            if config_file.exists():
                try:
                    content = config_file.read_text()
                    
                    # Extract DatabaseConfig class
                    db_config_match = re.search(
                        r'class DatabaseConfig\(BaseSettings\):(.*?)(?=class|\Z)',
                        content,
                        re.DOTALL
                    )
                    
                    if db_config_match:
                        db_config_content = db_config_match.group(1).strip()
                        
                        # Create a simplified pattern for comparison
                        pattern = re.sub(r'\s+', ' ', db_config_content)
                        pattern = re.sub(r'#.*', '', pattern)  # Remove comments
                        
                        if pattern not in config_patterns:
                            config_patterns[pattern] = []
                        config_patterns[pattern].append(service_path)
                        
                except Exception as e:
                    logger.error(f"❌ Error analyzing {config_file}: {e}")
                    self.consolidation_report["errors"].append(f"Analysis error in {config_file}: {e}")
        
        # Find duplicates
        duplicates = {pattern: services for pattern, services in config_patterns.items() 
                     if len(services) > 1}
        
        logger.info(f"📊 Found {len(duplicates)} duplicate database config patterns")
        return duplicates

    def create_service_specific_configs(self) -> None:
        """Create service-specific config files that inherit from shared base."""
        logger.info("🔧 Creating service-specific configurations...")
        
        for service_path in self.services_with_db_config:
            config_file = self.project_root / service_path / "config.py"
            if config_file.exists():
                try:
                    # Read current config
                    content = config_file.read_text()
                    
                    # Extract service name
                    service_name = service_path.split('/')[-1].replace('_service_standardized', '').replace('-', '_')
                    
                    # Create new config content that inherits from shared base
                    new_config_content = f'''"""
{service_name.title()} Service Configuration
Constitutional Hash: {self.constitutional_hash}

Inherits from shared ACGS configuration patterns.
"""

from pydantic import BaseSettings, Field
from services.shared.config.database_config import SharedDatabaseConfig

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "{self.constitutional_hash}"


class DatabaseConfig(SharedDatabaseConfig):
    """Database configuration for {service_name} service."""
    
    # Service-specific overrides can be added here if needed
    pass


class RedisConfig(BaseSettings):
    """Redis configuration settings."""
    
    constitutional_hash: str = "{self.constitutional_hash}"
    
    # Connection settings
    url: str = Field(
        default="redis://localhost:6389/0",
        env="REDIS_URL",
        description="Redis connection URL",
    )
    
    # Connection pool settings
    max_connections: int = Field(
        default=100,
        env="REDIS_MAX_CONNECTIONS",
        description="Maximum Redis connections",
    )
    
    socket_timeout: float = Field(
        default=5.0,
        env="REDIS_SOCKET_TIMEOUT",
        description="Socket timeout in seconds",
    )
    
    socket_connect_timeout: float = Field(
        default=5.0,
        env="REDIS_SOCKET_CONNECT_TIMEOUT", 
        description="Socket connect timeout in seconds",
    )


class ServiceConfig(BaseSettings):
    """Main service configuration."""
    
    constitutional_hash: str = "{self.constitutional_hash}"
    
    # Service identification
    service_name: str = "{service_name}"
    service_version: str = "1.0.0"
    
    # Server settings
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Performance settings
    workers: int = Field(default=1, env="WORKERS")
    max_requests: int = Field(default=1000, env="MAX_REQUESTS")
    
    # Security settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database and Redis configs
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    
    class Config:
        env_prefix = "ACGS_{service_name.upper()}_"
        case_sensitive = False


# Global config instance
config = ServiceConfig()
'''
                    
                    # Backup original file
                    backup_file = config_file.with_suffix('.py.backup')
                    shutil.copy2(config_file, backup_file)
                    
                    # Write new config
                    config_file.write_text(new_config_content)
                    
                    logger.info(f"✅ Updated config for {service_name}")
                    self.consolidation_report["services_updated"].append(service_path)
                    
                except Exception as e:
                    logger.error(f"❌ Error updating {config_file}: {e}")
                    self.consolidation_report["errors"].append(f"Update error in {config_file}: {e}")

    def create_shared_monitoring_base(self) -> None:
        """Create shared monitoring base classes."""
        logger.info("🔧 Creating shared monitoring base...")
        
        monitoring_dir = self.project_root / "services/shared/monitoring"
        monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        base_health_check_content = f'''"""
Shared Health Check Base Classes
Constitutional Hash: {self.constitutional_hash}
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

# Constitutional compliance
CONSTITUTIONAL_HASH = "{self.constitutional_hash}"


class HealthStatus(str, Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result data structure."""
    name: str
    status: HealthStatus
    message: str
    timestamp: float = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class BaseHealthCheck(ABC):
    """Base class for all health checks."""
    
    def __init__(self, name: str, critical: bool = False):
        self.name = name
        self.critical = critical
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform the health check."""
        pass
    
    def is_critical(self) -> bool:
        """Check if this health check is critical."""
        return self.critical


class ServiceHealthCheck(BaseHealthCheck):
    """Health check for ACGS services."""
    
    def __init__(self, name: str, service_url: str, critical: bool = True):
        super().__init__(name, critical)
        self.service_url = service_url
    
    async def check(self) -> HealthCheckResult:
        """Check service health via HTTP endpoint."""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{{self.service_url}}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.HEALTHY,
                            message=f"Service {{self.name}} is healthy",
                            details=data
                        )
                    else:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.UNHEALTHY,
                            message=f"Service {{self.name}} returned status {{response.status}}",
                            error=f"HTTP {{response.status}}"
                        )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Service {{self.name}} health check failed",
                error=str(e)
            )


class HealthCheckRegistry:
    """Registry for managing health checks."""
    
    def __init__(self):
        self.checks: Dict[str, BaseHealthCheck] = {{}}
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    def register(self, health_check: BaseHealthCheck) -> None:
        """Register a health check."""
        self.checks[health_check.name] = health_check
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {{}}
        
        for name, check in self.checks.items():
            try:
                result = await check.check()
                results[name] = result
            except Exception as e:
                results[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check {{name}} failed to execute",
                    error=str(e)
                )
        
        return results
    
    async def run_critical_checks(self) -> Dict[str, HealthCheckResult]:
        """Run only critical health checks."""
        results = {{}}
        
        for name, check in self.checks.items():
            if check.is_critical():
                try:
                    result = await check.check()
                    results[name] = result
                except Exception as e:
                    results[name] = HealthCheckResult(
                        name=name,
                        status=HealthStatus.UNKNOWN,
                        message=f"Critical health check {{name}} failed",
                        error=str(e)
                    )
        
        return results


# Global health check registry
_global_registry = HealthCheckRegistry()


def get_health_registry() -> HealthCheckRegistry:
    """Get the global health check registry."""
    return _global_registry
'''
        
        base_health_file = monitoring_dir / "base_health_checks.py"
        base_health_file.write_text(base_health_check_content)
        
        logger.info(f"✅ Created shared monitoring base: {base_health_file}")
        self.consolidation_report["shared_configs_created"].append(str(base_health_file))

    def generate_consolidation_report(self) -> None:
        """Generate consolidation report."""
        report_path = self.project_root / "reports" / f"functional_duplicate_consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        import json
        report_path.write_text(json.dumps(self.consolidation_report, indent=2))
        logger.info(f"📊 Consolidation report generated: {report_path}")

    def execute_consolidation(self) -> None:
        """Execute functional duplicate consolidation."""
        logger.info(f"🚀 Starting ACGS-2 Functional Duplicate Consolidation (Constitutional Hash: {self.constitutional_hash})")
        
        try:
            # Analyze current duplicates
            duplicates = self.analyze_database_config_duplicates()
            
            # Create service-specific configs that inherit from shared base
            self.create_service_specific_configs()
            
            # Create shared monitoring base
            self.create_shared_monitoring_base()
            
            # Generate report
            self.generate_consolidation_report()
            
            if not self.consolidation_report["errors"]:
                logger.info("🎉 Functional duplicate consolidation completed successfully!")
            else:
                logger.warning("⚠️ Consolidation completed with warnings. Check report for details.")
                
        except Exception as e:
            logger.error(f"❌ Consolidation failed: {e}")
            raise


def main():
    """Main execution function."""
    consolidator = ACGSFunctionalDuplicateConsolidator()
    consolidator.execute_consolidation()


if __name__ == "__main__":
    main()
