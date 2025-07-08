"""
ACGS Cache Configuration Loader
Constitutional Hash: cdd01ef066bc6cf2

Central loader for cache configurations using the cache optimization registry.
Provides standardized cache configuration loading across all ACGS services.
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Cache configuration for ACGS services"""

    service_name: str
    cache_type: str
    ttl_seconds: int
    max_size: int
    warming_keys: list[str]
    l1_memory_cache: dict[str, Any]
    l2_redis_cache: dict[str, Any]
    performance_targets: dict[str, float]
    monitoring: dict[str, bool]
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class CacheStrategy:
    """Cache strategy configuration"""

    multi_tier_enabled: bool
    cache_warming_enabled: bool
    warming_frequency_minutes: int
    constitutional_validation: bool = True


class CacheConfigLoader:
    """Central cache configuration loader for ACGS services"""

    def __init__(self, registry_path: str | None = None):
        """Initialize the cache config loader"""
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Default registry path
        if registry_path is None:
            current_dir = Path(__file__).parent
            registry_path = current_dir / "cache_optimization_registry.json"

        self.registry_path = Path(registry_path)
        self._registry_data: dict[str, Any] | None = None
        self._load_registry()

    def _load_registry(self) -> None:
        """Load the cache optimization registry"""
        try:
            if not self.registry_path.exists():
                logger.error(f"Cache registry not found: {self.registry_path}")
                self._registry_data = {}
                return

            with open(self.registry_path) as f:
                self._registry_data = json.load(f)

            # Validate constitutional hash
            registry_hash = self._registry_data.get("constitutional_hash")
            if registry_hash != self.constitutional_hash:
                logger.warning(
                    "Constitutional hash mismatch in cache registry: "
                    f"{registry_hash} != {self.constitutional_hash}"
                )

            logger.info(f"Cache registry loaded successfully: {self.registry_path}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in cache registry: {e}")
            self._registry_data = {}
        except Exception as e:
            logger.error(f"Failed to load cache registry: {e}")
            self._registry_data = {}

    def get_service_cache_config(self, service_name: str) -> CacheConfig | None:
        """Get cache configuration for a specific service"""
        if not self._registry_data:
            logger.warning("Cache registry not loaded")
            return None

        services = self._registry_data.get("services", {})
        service_config = services.get(service_name)

        if not service_config:
            logger.warning(f"No cache config found for service: {service_name}")
            return self._create_default_config(service_name)

        # Get default settings
        defaults = self._registry_data.get("default_settings", {})

        # Merge service-specific with defaults
        config = CacheConfig(
            service_name=service_config["service_name"],
            cache_type=service_config["cache_type"],
            ttl_seconds=service_config["ttl_seconds"],
            max_size=service_config["max_size"],
            warming_keys=service_config["warming_keys"],
            l1_memory_cache=defaults.get("cache_strategies", {}).get(
                "l1_memory_cache", {}
            ),
            l2_redis_cache={
                "enabled": True,
                "max_size": service_config["max_size"],
                "ttl_seconds": service_config["ttl_seconds"],
            },
            performance_targets=defaults.get("performance_targets", {}),
            monitoring=defaults.get("monitoring", {}),
            constitutional_hash=self.constitutional_hash,
        )

        logger.debug(f"Loaded cache config for {service_name}: {config.cache_type}")
        return config

    def get_cache_strategy(self, service_name: str, cache_type: str) -> CacheStrategy:
        """Get cache strategy for a service and cache type"""
        config = self.get_service_cache_config(service_name)

        if not config:
            return self._create_default_strategy()

        defaults = self._registry_data.get("default_settings", {})
        cache_strategies = defaults.get("cache_strategies", {})

        strategy = CacheStrategy(
            multi_tier_enabled=cache_strategies.get("multi_tier_enabled", True),
            cache_warming_enabled=bool(config.warming_keys),
            warming_frequency_minutes=cache_strategies.get(
                "warming_frequency_minutes", 30
            ),
            constitutional_validation=True,
        )

        return strategy

    def _create_default_config(self, service_name: str) -> CacheConfig:
        """Create default cache configuration for unknown services"""
        logger.info(f"Creating default cache config for: {service_name}")

        return CacheConfig(
            service_name=service_name,
            cache_type="generic",
            ttl_seconds=3600,  # 1 hour default
            max_size=1000,
            warming_keys=[],
            l1_memory_cache={"enabled": True, "max_size": 1000, "ttl_seconds": 300},
            l2_redis_cache={"enabled": True, "max_size": 1000, "ttl_seconds": 3600},
            performance_targets={"hit_rate_target": 0.85, "latency_target_ms": 2.0},
            monitoring={"metrics_enabled": True, "hit_rate_alerts": True},
            constitutional_hash=self.constitutional_hash,
        )

    def _create_default_strategy(self) -> CacheStrategy:
        """Create default cache strategy"""
        return CacheStrategy(
            multi_tier_enabled=True,
            cache_warming_enabled=False,
            warming_frequency_minutes=30,
            constitutional_validation=True,
        )

    def get_all_service_configs(self) -> dict[str, CacheConfig]:
        """Get cache configurations for all services"""
        if not self._registry_data:
            return {}

        services = self._registry_data.get("services", {})
        configs = {}

        for service_name in services.keys():
            config = self.get_service_cache_config(service_name)
            if config:
                configs[service_name] = config

        return configs

    def validate_constitutional_compliance(self) -> dict[str, Any]:
        """Validate constitutional compliance of cache configurations"""
        compliance_report = {
            "compliant": True,
            "constitutional_hash": self.constitutional_hash,
            "services_checked": 0,
            "issues": [],
        }

        if not self._registry_data:
            compliance_report["compliant"] = False
            compliance_report["issues"].append("Cache registry not loaded")
            return compliance_report

        # Check registry constitutional hash
        registry_hash = self._registry_data.get("constitutional_hash")
        if registry_hash != self.constitutional_hash:
            compliance_report["compliant"] = False
            compliance_report["issues"].append(
                f"Registry constitutional hash mismatch: {registry_hash}"
            )

        # Check each service config
        services = self._registry_data.get("services", {})
        compliance_report["services_checked"] = len(services)

        for service_name, service_config in services.items():
            config = self.get_service_cache_config(service_name)
            if config and config.constitutional_hash != self.constitutional_hash:
                compliance_report["compliant"] = False
                compliance_report["issues"].append(
                    f"Service {service_name} constitutional hash mismatch"
                )

        return compliance_report

    def reload_registry(self) -> bool:
        """Reload the cache registry from disk"""
        try:
            self._load_registry()
            return True
        except Exception as e:
            logger.error(f"Failed to reload cache registry: {e}")
            return False


# Global cache config loader instance
_cache_loader: CacheConfigLoader | None = None


def get_cache_loader() -> CacheConfigLoader:
    """Get the global cache configuration loader instance"""
    global _cache_loader
    if _cache_loader is None:
        _cache_loader = CacheConfigLoader()
    return _cache_loader


def load_service_cache_config(service_name: str) -> CacheConfig | None:
    """Convenience function to load cache config for a service"""
    loader = get_cache_loader()
    return loader.get_service_cache_config(service_name)


def get_service_cache_strategy(service_name: str, cache_type: str) -> CacheStrategy:
    """Convenience function to get cache strategy for a service"""
    loader = get_cache_loader()
    return loader.get_cache_strategy(service_name, cache_type)
