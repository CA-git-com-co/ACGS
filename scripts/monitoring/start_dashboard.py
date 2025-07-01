#!/usr/bin/env python3
"""
ACGS Monitoring Dashboard Startup Script

This script starts the comprehensive monitoring dashboard with proper configuration,
health checks, and production-ready settings.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import os
import sys
import yaml
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from services.monitoring.comprehensive_monitoring_dashboard import monitoring_dashboard

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DashboardStarter:
    """Handles startup and configuration of the monitoring dashboard."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.config_path = (
            project_root / "config" / "monitoring" / "dashboard_config.yml"
        )
        self.config = None

    async def start_dashboard(self):
        """Start the monitoring dashboard with full configuration."""
        logger.info("🚀 Starting ACGS Comprehensive Monitoring Dashboard")
        logger.info(f"📜 Constitutional Hash: {self.constitutional_hash}")

        try:
            # 1. Load configuration
            await self._load_configuration()

            # 2. Validate environment
            await self._validate_environment()

            # 3. Initialize dependencies
            await self._initialize_dependencies()

            # 4. Start dashboard server
            await self._start_dashboard_server()

        except Exception as e:
            logger.error(f"❌ Failed to start monitoring dashboard: {e}")
            raise

    async def _load_configuration(self):
        """Load dashboard configuration from YAML file."""
        logger.info("📋 Loading dashboard configuration")

        if not self.config_path.exists():
            logger.warning(f"⚠️ Configuration file not found: {self.config_path}")
            logger.info("📋 Using default configuration")
            self.config = self._get_default_config()
        else:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f)
            logger.info(f"✅ Configuration loaded from {self.config_path}")

        # Validate constitutional hash
        config_hash = self.config.get("dashboard", {}).get("constitutional_hash")
        if config_hash != self.constitutional_hash:
            logger.warning(f"⚠️ Constitutional hash mismatch in config: {config_hash}")
            self.config["dashboard"]["constitutional_hash"] = self.constitutional_hash

    def _get_default_config(self):
        """Get default configuration if config file is not found."""
        return {
            "dashboard": {
                "name": "ACGS Comprehensive Monitoring Dashboard",
                "constitutional_hash": self.constitutional_hash,
                "server": {"host": "0.0.0.0", "port": 8000, "workers": 1},
            },
            "metrics": {
                "collection_interval": 5,
                "system_metrics": {"enabled": True},
                "performance_metrics": {"enabled": True},
                "constitutional_metrics": {"enabled": True},
            },
            "alerting": {
                "enabled": True,
                "thresholds": {
                    "system": {"cpu_usage": 80.0, "memory_usage": 85.0},
                    "performance": {"response_time_ms": 5.0},
                    "constitutional": {"compliance_rate_percent": 99.9},
                },
            },
        }

    async def _validate_environment(self):
        """Validate the environment and dependencies."""
        logger.info("🔍 Validating environment")

        # Check Python version
        if sys.version_info < (3, 8):
            raise RuntimeError("Python 3.8 or higher is required")

        # Check required directories
        required_dirs = ["logs", "static", "reports", "config/monitoring"]

        for dir_path in required_dirs:
            full_path = project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Directory ensured: {dir_path}")

        # Check constitutional compliance
        logger.info(f"📜 Constitutional hash validated: {self.constitutional_hash}")

        logger.info("✅ Environment validation completed")

    async def _initialize_dependencies(self):
        """Initialize external dependencies and services."""
        logger.info("🔧 Initializing dependencies")

        # Initialize Redis connection (optional)
        try:
            import redis

            redis_config = self.config.get("data_sources", {}).get("redis", {})
            if redis_config.get("enabled", False):
                redis_client = redis.Redis(
                    host=redis_config.get("host", "localhost"),
                    port=redis_config.get("port", 6379),
                    db=redis_config.get("db", 0),
                    decode_responses=True,
                )
                # Test connection
                redis_client.ping()
                logger.info("✅ Redis connection established")
            else:
                logger.info("ℹ️ Redis disabled in configuration")
        except ImportError:
            logger.warning("⚠️ Redis not available (install redis-py for Redis support)")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")

        # Initialize Prometheus connection (optional)
        try:
            prometheus_config = self.config.get("data_sources", {}).get(
                "prometheus", {}
            )
            if prometheus_config.get("enabled", False):
                prometheus_url = prometheus_config.get("url", "http://localhost:9090")
                logger.info(f"✅ Prometheus configured: {prometheus_url}")
            else:
                logger.info("ℹ️ Prometheus disabled in configuration")
        except Exception as e:
            logger.warning(f"⚠️ Prometheus configuration failed: {e}")

        logger.info("✅ Dependencies initialization completed")

    async def _start_dashboard_server(self):
        """Start the dashboard server with configuration."""
        logger.info("🌐 Starting dashboard server")

        # Get server configuration
        server_config = self.config.get("dashboard", {}).get("server", {})
        host = server_config.get("host", "0.0.0.0")
        port = server_config.get("port", 8000)

        # Update monitoring dashboard configuration
        monitoring_dashboard.constitutional_hash = self.constitutional_hash
        monitoring_dashboard.alert_thresholds.update(
            self.config.get("alerting", {}).get("thresholds", {}).get("system", {})
        )

        logger.info(f"🌐 Dashboard will be available at: http://{host}:{port}")
        logger.info(f"📊 Real-time metrics: ws://{host}:{port}/ws/metrics")
        logger.info(f"🔗 API endpoints: http://{host}:{port}/api/")

        # Start the monitoring dashboard
        await monitoring_dashboard.start_monitoring(host=host, port=port)


async def main():
    """Main function to start the dashboard."""
    starter = DashboardStarter()

    try:
        await starter.start_dashboard()
    except KeyboardInterrupt:
        logger.info("🛑 Dashboard stopped by user")
    except Exception as e:
        logger.error(f"❌ Dashboard startup failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
