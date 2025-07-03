"""
ACGS E2E Test Configuration Management

Provides configuration management for different testing modes and environments,
supporting online, offline, and hybrid testing scenarios.
"""

import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, ConfigDict


class E2ETestMode(str, Enum):
    """Test execution modes for E2E testing."""
    ONLINE = "online"      # Test against live infrastructure
    OFFLINE = "offline"    # Use mocked services and in-memory databases
    HYBRID = "hybrid"      # Mix of live and mocked components


class ServiceType(str, Enum):
    """ACGS service types."""
    AUTH = "auth"
    CONSTITUTIONAL_AI = "ac"
    INTEGRITY = "integrity"
    FORMAL_VERIFICATION = "fv"
    GOVERNANCE_SYNTHESIS = "gs"
    POLICY_GOVERNANCE = "pgc"
    EVOLUTIONARY_COMPUTATION = "ec"
    AGENT_HITL = "agent_hitl"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    name: str
    port: int
    host: str = "localhost"
    health_path: str = "/health"
    protocol: str = "http"
    
    @property
    def url(self) -> str:
        """Get full service URL."""
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property
    def health_url(self) -> str:
        """Get health check URL."""
        return f"{self.url}{self.health_path}"


@dataclass
class PerformanceTargets:
    """Performance targets for validation."""
    p99_latency_ms: float = 5.0
    cache_hit_rate: float = 0.85
    throughput_rps: float = 100.0
    success_rate: float = 0.95
    resource_utilization: float = 0.80
    test_coverage: float = 0.80


@dataclass
class InfrastructureConfig:
    """Infrastructure component configuration."""
    postgresql_host: str = "localhost"
    postgresql_port: int = 5439
    postgresql_database: str = "acgs_test"
    postgresql_user: str = "test_user"
    postgresql_password: str = "test_password"
    
    redis_host: str = "localhost"
    redis_port: int = 6389
    redis_database: int = 0
    
    auth_service_port: int = 8016
    
    @property
    def postgresql_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return (
            f"postgresql+asyncpg://{self.postgresql_user}:"
            f"{self.postgresql_password}@{self.postgresql_host}:"
            f"{self.postgresql_port}/{self.postgresql_database}"
        )
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_database}"


class E2ETestConfig(BaseModel):
    """Comprehensive E2E test configuration."""
    
    # Core configuration
    test_mode: E2ETestMode = E2ETestMode.OFFLINE
    constitutional_hash: str = "cdd01ef066bc6cf2"
    project_root: Path = Field(default_factory=lambda: Path.cwd())
    
    # Service endpoints
    services: Dict[ServiceType, ServiceEndpoint] = Field(default_factory=dict)
    
    # Infrastructure
    infrastructure: InfrastructureConfig = Field(default_factory=InfrastructureConfig)
    
    # Performance targets
    performance: PerformanceTargets = Field(default_factory=PerformanceTargets)
    
    # Test execution settings
    parallel_workers: int = 4
    test_timeout_seconds: int = 300
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    
    # Reporting
    report_directory: Path = Field(default_factory=lambda: Path("reports/e2e"))
    junit_xml_path: Optional[Path] = None
    coverage_report: bool = True
    performance_report: bool = True
    
    # Environment-specific overrides
    environment: str = "test"
    debug_mode: bool = False
    verbose_logging: bool = True
    
    model_config = ConfigDict(
        use_enum_values=True,
        arbitrary_types_allowed=True
    )
    
    def __post_init__(self):
        """Initialize default service endpoints."""
        if not self.services:
            self._setup_default_services()
    
    def _setup_default_services(self):
        """Setup default ACGS service endpoints."""
        default_services = {
            ServiceType.AUTH: ServiceEndpoint("auth_service", 8016),
            ServiceType.CONSTITUTIONAL_AI: ServiceEndpoint("ac_service", 8001),
            ServiceType.INTEGRITY: ServiceEndpoint("integrity_service", 8002),
            ServiceType.FORMAL_VERIFICATION: ServiceEndpoint("fv_service", 8003),
            ServiceType.GOVERNANCE_SYNTHESIS: ServiceEndpoint("gs_service", 8004),
            ServiceType.POLICY_GOVERNANCE: ServiceEndpoint("pgc_service", 8005),
            ServiceType.EVOLUTIONARY_COMPUTATION: ServiceEndpoint("ec_service", 8006),
            ServiceType.AGENT_HITL: ServiceEndpoint("agent_hitl_service", 8008),
        }
        self.services = default_services
    
    @classmethod
    def from_environment(cls) -> "E2ETestConfig":
        """Create configuration from environment variables."""
        config = cls()
        
        # Override from environment
        if mode := os.getenv("E2E_TEST_MODE"):
            config.test_mode = E2ETestMode(mode)
        
        if hash_val := os.getenv("CONSTITUTIONAL_HASH"):
            config.constitutional_hash = hash_val
        
        if workers := os.getenv("E2E_PARALLEL_WORKERS"):
            config.parallel_workers = int(workers)
        
        if timeout := os.getenv("E2E_TEST_TIMEOUT"):
            config.test_timeout_seconds = int(timeout)
        
        # Infrastructure overrides
        if pg_host := os.getenv("POSTGRES_HOST"):
            config.infrastructure.postgresql_host = pg_host
        
        if pg_port := os.getenv("POSTGRES_PORT"):
            config.infrastructure.postgresql_port = int(pg_port)
        
        if redis_host := os.getenv("REDIS_HOST"):
            config.infrastructure.redis_host = redis_host
        
        if redis_port := os.getenv("REDIS_PORT"):
            config.infrastructure.redis_port = int(redis_port)
        
        return config
    
    def get_service_url(self, service_type: ServiceType) -> str:
        """Get URL for a specific service."""
        if service_type not in self.services:
            raise ValueError(f"Service {service_type} not configured")
        return self.services[service_type].url
    
    def is_service_enabled(self, service_type: ServiceType) -> bool:
        """Check if a service is enabled for testing."""
        return service_type in self.services
    
    def get_test_database_url(self) -> str:
        """Get test database URL with unique database name."""
        base_db = self.infrastructure.postgresql_database
        test_db = f"{base_db}_e2e_{os.getpid()}"
        
        return (
            f"postgresql+asyncpg://{self.infrastructure.postgresql_user}:"
            f"{self.infrastructure.postgresql_password}@"
            f"{self.infrastructure.postgresql_host}:"
            f"{self.infrastructure.postgresql_port}/{test_db}"
        )
