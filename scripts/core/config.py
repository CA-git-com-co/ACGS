"""
ACGS Configuration Management
Constitutional Hash: cdd01ef066bc6cf2

Unified configuration system for ACGS scripts.
"""

import os
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional, List
from .exceptions import ConfigurationError

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class ServiceConfig:
    """Configuration for individual ACGS services."""
    name: str
    host: str = "localhost"
    port: int = 8000
    protocol: str = "http"
    timeout: int = 30
    max_retries: int = 3
    health_endpoint: str = "/health"
    
    @property
    def base_url(self) -> str:
        """Get the base URL for the service."""
        return f"{self.protocol}://{self.host}:{self.port}"
    
    @property 
    def health_url(self) -> str:
        """Get the health check URL for the service."""
        return f"{self.base_url}{self.health_endpoint}"


@dataclass
class DatabaseConfig:
    """Database configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "acgs"
    username: str = "acgs_user"
    password: str = ""
    max_connections: int = 10
    timeout: int = 30


@dataclass 
class RedisConfig:
    """Redis configuration."""
    host: str = "localhost"
    port: int = 6379
    database: int = 0
    password: str = ""
    timeout: int = 10


@dataclass
class Config:
    """Main ACGS configuration."""
    
    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    # Environment
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # Services
    services: Dict[str, ServiceConfig] = field(default_factory=dict)
    
    # Database
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Redis  
    redis: RedisConfig = field(default_factory=RedisConfig)
    
    # Performance targets
    target_p99_latency_ms: float = 5.0
    target_throughput_rps: int = 100
    
    # Validation settings
    validation_timeout: int = 60
    max_concurrent_validations: int = 10
    
    # Testing settings
    test_timeout: int = 300
    test_parallel_workers: int = 4
    
    def __post_init__(self):
        """Initialize default services if not provided."""
        if not self.services:
            self._init_default_services()
    
    def _init_default_services(self):
        """Initialize default ACGS service configurations."""
        default_services = {
            "constitutional-ai": ServiceConfig("constitutional-ai", port=8001),
            "integrity": ServiceConfig("integrity", port=8002),
            "evolutionary-computation": ServiceConfig("evolutionary-computation", port=8013), 
            "formal-verification": ServiceConfig("formal-verification", port=8011),
            "policy-governance": ServiceConfig("policy-governance", port=8014),
            "coordinator": ServiceConfig("coordinator", port=8008),
            "workers": ServiceConfig("workers", port=8009),
            "blackboard": ServiceConfig("blackboard", port=8010),
            "auth": ServiceConfig("auth", port=8016),
            "api-gateway": ServiceConfig("api-gateway", port=8017),
        }
        self.services.update(default_services)
    
    def get_service(self, name: str) -> ServiceConfig:
        """Get service configuration by name."""
        if name not in self.services:
            raise ConfigurationError(f"Service '{name}' not found in configuration")
        return self.services[name]
    
    def get_all_services(self) -> List[ServiceConfig]:
        """Get all service configurations."""
        return list(self.services.values())
    
    def validate(self) -> None:
        """Validate configuration."""
        if self.constitutional_hash != CONSTITUTIONAL_HASH:
            raise ConfigurationError(
                f"Invalid constitutional hash: {self.constitutional_hash}. "
                f"Expected: {CONSTITUTIONAL_HASH}"
            )
        
        if self.target_p99_latency_ms <= 0:
            raise ConfigurationError("target_p99_latency_ms must be positive")
        
        if self.target_throughput_rps <= 0:
            raise ConfigurationError("target_throughput_rps must be positive")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create configuration from environment variables."""
        config = cls()
        
        # Environment settings
        config.environment = os.getenv("ACGS_ENVIRONMENT", config.environment)
        config.debug = os.getenv("ACGS_DEBUG", "false").lower() == "true"
        config.log_level = os.getenv("ACGS_LOG_LEVEL", config.log_level)
        
        # Performance targets
        if p99_latency := os.getenv("ACGS_TARGET_P99_LATENCY_MS"):
            config.target_p99_latency_ms = float(p99_latency)
        
        if throughput := os.getenv("ACGS_TARGET_THROUGHPUT_RPS"):
            config.target_throughput_rps = int(throughput)
        
        # Database
        if db_host := os.getenv("ACGS_DB_HOST"):
            config.database.host = db_host
        if db_port := os.getenv("ACGS_DB_PORT"):
            config.database.port = int(db_port)
        if db_name := os.getenv("ACGS_DB_NAME"):
            config.database.database = db_name
        if db_user := os.getenv("ACGS_DB_USER"):
            config.database.username = db_user
        if db_pass := os.getenv("ACGS_DB_PASSWORD"):
            config.database.password = db_pass
        
        # Redis
        if redis_host := os.getenv("ACGS_REDIS_HOST"):
            config.redis.host = redis_host
        if redis_port := os.getenv("ACGS_REDIS_PORT"):
            config.redis.port = int(redis_port)
        if redis_db := os.getenv("ACGS_REDIS_DB"):
            config.redis.database = int(redis_db)
        if redis_pass := os.getenv("ACGS_REDIS_PASSWORD"):
            config.redis.password = redis_pass
        
        config.validate()
        return config
    
    @classmethod
    def from_file(cls, config_path: Path) -> "Config":
        """Load configuration from JSON file."""
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
            
            config = cls()
            
            # Update from file data
            for key, value in data.items():
                if hasattr(config, key):
                    if key == "services":
                        # Handle services specially
                        for service_name, service_data in value.items():
                            config.services[service_name] = ServiceConfig(**service_data)
                    elif key == "database":
                        config.database = DatabaseConfig(**value)
                    elif key == "redis":
                        config.redis = RedisConfig(**value)
                    else:
                        setattr(config, key, value)
            
            config.validate()
            return config
            
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ConfigurationError(f"Invalid configuration file: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "constitutional_hash": self.constitutional_hash,
            "environment": self.environment,
            "debug": self.debug,
            "log_level": self.log_level,
            "services": {
                name: {
                    "name": svc.name,
                    "host": svc.host,
                    "port": svc.port,
                    "protocol": svc.protocol,
                    "timeout": svc.timeout,
                    "max_retries": svc.max_retries,
                    "health_endpoint": svc.health_endpoint,
                }
                for name, svc in self.services.items()
            },
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "username": self.database.username,
                "max_connections": self.database.max_connections,
                "timeout": self.database.timeout,
            },
            "redis": {
                "host": self.redis.host,
                "port": self.redis.port,
                "database": self.redis.database,
                "timeout": self.redis.timeout,
            },
            "target_p99_latency_ms": self.target_p99_latency_ms,
            "target_throughput_rps": self.target_throughput_rps,
            "validation_timeout": self.validation_timeout,
            "max_concurrent_validations": self.max_concurrent_validations,
            "test_timeout": self.test_timeout,
            "test_parallel_workers": self.test_parallel_workers,
        }


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        # Try to load from file first, then from environment
        config_file = Path(__file__).parent.parent / "config.json"
        if config_file.exists():
            _config = Config.from_file(config_file)
        else:
            _config = Config.from_env()
    return _config


def set_config(config: Config) -> None:
    """Set global configuration instance."""
    global _config
    config.validate()
    _config = config