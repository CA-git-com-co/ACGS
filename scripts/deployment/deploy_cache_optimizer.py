#!/usr/bin/env python3
"""
ACGS Cache Performance Optimizer Deployment Script
Constitutional Hash: cdd01ef066bc6cf2

Deploys the cache performance optimizer across all ACGS services.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from tools.acgs_cache_performance_optimizer import (
    CACHE_OPTIMIZATION_CONFIG,
    CONSTITUTIONAL_HASH,
    OptimizedCacheManager,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / "logs" / "cache_deployment.log"),
    ],
)
logger = logging.getLogger(__name__)


class CacheOptimizerDeployment:
    """Manages deployment of cache optimization across ACGS services."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.deployed_services = []
        self.deployment_results = {
            "constitutional_hash": self.constitutional_hash,
            "deployment_time": datetime.utcnow().isoformat(),
            "services": {},
            "overall_status": "pending",
            "performance_targets": CACHE_OPTIMIZATION_CONFIG,
        }

        # ACGS services to optimize
        self.target_services = [
            {
                "name": "constitutional-ai",
                "description": "Core constitutional compliance service",
                "priority": "high",
                "cache_types": [
                    "constitutional_hash",
                    "validation_results",
                    "compliance_checks",
                ],
            },
            {
                "name": "api-gateway",
                "description": "API Gateway service",
                "priority": "high",
                "cache_types": [
                    "user_sessions",
                    "policy_decisions",
                    "performance_metrics",
                ],
            },
            {
                "name": "integrity",
                "description": "Audit and integrity service",
                "priority": "medium",
                "cache_types": ["audit_logs", "governance_rules"],
            },
            {
                "name": "governance-synthesis",
                "description": "Governance synthesis service",
                "priority": "medium",
                "cache_types": ["governance_rules", "policy_decisions"],
            },
            {
                "name": "multi-agent-coordinator",
                "description": "Multi-agent coordination service",
                "priority": "medium",
                "cache_types": ["performance_metrics", "validation_results"],
            },
        ]

    async def deploy_cache_optimization(self) -> dict[str, Any]:
        """Deploy cache optimization to all target services."""
        logger.info("🚀 Starting ACGS Cache Optimization Deployment")
        logger.info(f"📋 Constitutional Hash: {self.constitutional_hash}")
        logger.info(
            f"🎯 Target Hit Rate: {CACHE_OPTIMIZATION_CONFIG['target_hit_rate'] * 100}%"
        )

        try:
            # Create logs directory if it doesn't exist
            os.makedirs(project_root / "logs", exist_ok=True)

            # Deploy to each service
            for service_config in self.target_services:
                service_result = await self._deploy_to_service(service_config)
                self.deployment_results["services"][
                    service_config["name"]
                ] = service_result

                if service_result["status"] == "success":
                    self.deployed_services.append(service_config["name"])

            # Test overall performance
            overall_metrics = await self._test_overall_performance()
            self.deployment_results["overall_metrics"] = overall_metrics

            # Determine overall status
            success_count = len([
                r
                for r in self.deployment_results["services"].values()
                if r["status"] == "success"
            ])
            total_count = len(self.target_services)

            if success_count == total_count:
                self.deployment_results["overall_status"] = "success"
                logger.info("✅ Cache optimization deployment completed successfully")
            elif success_count > total_count // 2:
                self.deployment_results["overall_status"] = "partial_success"
                logger.warning(
                    "⚠️ Cache optimization partially deployed"
                    f" ({success_count}/{total_count})"
                )
            else:
                self.deployment_results["overall_status"] = "failed"
                logger.error(
                    "❌ Cache optimization deployment failed"
                    f" ({success_count}/{total_count})"
                )

            # Save deployment report
            await self._save_deployment_report()

            return self.deployment_results

        except Exception as e:
            logger.error(f"Deployment error: {e}")
            self.deployment_results["overall_status"] = "error"
            self.deployment_results["error"] = str(e)
            return self.deployment_results

    async def _deploy_to_service(
        self, service_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Deploy cache optimization to a specific service."""
        service_name = service_config["name"]
        logger.info(f"📦 Deploying cache optimization to {service_name}")

        result = {
            "status": "pending",
            "service_name": service_name,
            "deployment_time": datetime.utcnow().isoformat(),
            "constitutional_hash": self.constitutional_hash,
        }

        try:
            # Initialize cache manager for this service
            cache_manager = OptimizedCacheManager(service_name=service_name)

            # Test initialization
            if await cache_manager.initialize():
                logger.info(f"✅ Cache manager initialized for {service_name}")

                # Perform service-specific cache warming
                warming_results = await self._warm_service_cache(
                    cache_manager, service_config["cache_types"]
                )

                # Test cache operations
                test_results = await self._test_cache_operations(cache_manager)

                # Get baseline metrics
                metrics = await cache_manager.get_performance_metrics()

                # Update service configuration files
                config_updated = await self._update_service_config(service_config)

                result.update({
                    "status": "success",
                    "warming_results": warming_results,
                    "test_results": test_results,
                    "baseline_metrics": metrics,
                    "config_updated": config_updated,
                })

                logger.info(
                    f"✅ Cache optimization deployed successfully to {service_name}"
                )

                # Keep cache manager running for this service
                # In production, this would be integrated into the service startup
                await cache_manager.close()

            else:
                result.update({
                    "status": "failed", "error": "Cache manager initialization failed"
                })
                logger.error(
                    f"❌ Cache manager initialization failed for {service_name}"
                )

        except Exception as e:
            result.update({"status": "error", "error": str(e)})
            logger.error(f"❌ Deployment error for {service_name}: {e}")

        return result

    async def _warm_service_cache(
        self, cache_manager: OptimizedCacheManager, cache_types: list[str]
    ) -> dict[str, Any]:
        """Perform service-specific cache warming."""
        warming_results = {}

        try:
            # Warm general cache first
            general_warming = await cache_manager.warm_cache(
                "constitutional_compliance"
            )
            warming_results["constitutional_compliance"] = general_warming

            # Warm service-specific cache types
            for cache_type in cache_types:
                # Simulate warming for specific cache types
                test_keys = [
                    f"{cache_type}:test_key_1",
                    f"{cache_type}:test_key_2",
                    f"{cache_type}:common_pattern",
                ]

                warmed_count = 0
                for key in test_keys:
                    test_value = {
                        "cache_type": cache_type,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                        "warmed_at": datetime.utcnow().isoformat(),
                        "test_data": f"Optimized cache value for {key}",
                    }

                    if await cache_manager.set(key, test_value, cache_type):
                        warmed_count += 1

                warming_results[cache_type] = {"warmed_keys": warmed_count}

            logger.info(f"🔥 Cache warming completed: {warming_results}")
            return warming_results

        except Exception as e:
            logger.error(f"Cache warming error: {e}")
            return {"error": str(e)}

    async def _test_cache_operations(
        self, cache_manager: OptimizedCacheManager
    ) -> dict[str, Any]:
        """Test cache operations to validate deployment."""
        test_results = {
            "operations_tested": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "performance_test": {},
        }

        try:
            # Test basic operations
            operations = [
                (
                    "set",
                    "test_deployment_key",
                    {"test": "deployment_value"},
                    "test_data",
                ),
                ("get", "test_deployment_key", None, "test_data"),
                ("delete", "test_deployment_key", None, "test_data"),
            ]

            for op_type, key, value, data_type in operations:
                test_results["operations_tested"] += 1

                try:
                    if op_type == "set":
                        success = await cache_manager.set(key, value, data_type)
                    elif op_type == "get":
                        result = await cache_manager.get(key, data_type)
                        success = result is not None
                    elif op_type == "delete":
                        success = await cache_manager.delete(key, data_type)

                    if success:
                        test_results["successful_operations"] += 1
                    else:
                        test_results["failed_operations"] += 1

                except Exception as e:
                    test_results["failed_operations"] += 1
                    logger.warning(f"Cache operation {op_type} failed: {e}")

            # Performance test
            start_time = datetime.utcnow()

            # Rapid cache operations
            for i in range(100):
                await cache_manager.set(
                    f"perf_test_{i}", {"test_data": i}, "performance_test"
                )
                await cache_manager.get(f"perf_test_{i}", "performance_test")

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            test_results["performance_test"] = {
                "operations_count": 200,
                "duration_ms": duration_ms,
                "ops_per_second": 200 / (duration_ms / 1000),
                "avg_latency_ms": duration_ms / 200,
            }

            logger.info(f"🧪 Cache operations test completed: {test_results}")
            return test_results

        except Exception as e:
            logger.error(f"Cache operations test error: {e}")
            test_results["error"] = str(e)
            return test_results

    async def _update_service_config(self, service_config: dict[str, Any]) -> bool:
        """Update service configuration to enable cache optimization."""
        try:
            service_name = service_config["name"]

            # Create cache configuration for the service
            cache_config = {
                "cache_optimization": {
                    "enabled": True,
                    "constitutional_hash": self.constitutional_hash,
                    "target_hit_rate": CACHE_OPTIMIZATION_CONFIG["target_hit_rate"],
                    "service_specific": {
                        "cache_types": service_config["cache_types"],
                        "priority": service_config["priority"],
                    },
                }
            }

            # Save configuration file
            config_dir = project_root / "config" / "services" / service_name
            config_dir.mkdir(parents=True, exist_ok=True)

            config_file = config_dir / "cache_optimization.json"
            with open(config_file, "w") as f:
                json.dump(cache_config, f, indent=2)

            logger.info(f"📝 Updated configuration for {service_name}")
            return True

        except Exception as e:
            logger.error(
                f"Configuration update error for {service_config['name']}: {e}"
            )
            return False

    async def _test_overall_performance(self) -> dict[str, Any]:
        """Test overall cache performance across services."""
        logger.info("📊 Testing overall cache performance")

        overall_metrics = {
            "test_time": datetime.utcnow().isoformat(),
            "constitutional_hash": self.constitutional_hash,
            "services_tested": len(self.deployed_services),
            "aggregate_metrics": {},
        }

        try:
            # Test cache performance for each deployed service
            service_metrics = []

            for service_name in self.deployed_services:
                cache_manager = OptimizedCacheManager(service_name=service_name)

                if await cache_manager.initialize():
                    metrics = await cache_manager.get_performance_metrics()
                    service_metrics.append(metrics)
                    await cache_manager.close()

            if service_metrics:
                # Calculate aggregate metrics
                total_operations = sum(
                    m["cache_performance"]["total_operations"] for m in service_metrics
                )
                total_hits = sum(
                    m["cache_performance"]["hits"] for m in service_metrics
                )

                overall_hit_rate = (
                    total_hits / total_operations if total_operations > 0 else 0
                )

                overall_metrics["aggregate_metrics"] = {
                    "overall_hit_rate": round(overall_hit_rate, 4),
                    "overall_hit_rate_percent": round(overall_hit_rate * 100, 2),
                    "target_hit_rate": CACHE_OPTIMIZATION_CONFIG["target_hit_rate"],
                    "target_met": (
                        overall_hit_rate >= CACHE_OPTIMIZATION_CONFIG["target_hit_rate"]
                    ),
                    "total_operations": total_operations,
                    "total_hits": total_hits,
                    "services_count": len(service_metrics),
                }

            logger.info("📈 Overall performance test completed")
            return overall_metrics

        except Exception as e:
            logger.error(f"Overall performance test error: {e}")
            overall_metrics["error"] = str(e)
            return overall_metrics

    async def _save_deployment_report(self) -> None:
        """Save detailed deployment report."""
        try:
            report_dir = project_root / "reports"
            report_dir.mkdir(exist_ok=True)

            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"cache_optimization_deployment_{timestamp}.json"

            with open(report_file, "w") as f:
                json.dump(self.deployment_results, f, indent=2)

            logger.info(f"📋 Deployment report saved: {report_file}")

        except Exception as e:
            logger.error(f"Error saving deployment report: {e}")


async def main():
    """Main deployment function."""
    print("🚀 ACGS Cache Performance Optimizer Deployment")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)

    try:
        # Create deployment manager
        deployment = CacheOptimizerDeployment()

        # Execute deployment
        results = await deployment.deploy_cache_optimization()

        # Display results
        print("\n📊 Deployment Results:")
        print(f"Overall Status: {results['overall_status']}")
        print(
            "Services Deployed:"
            f" {len(deployment.deployed_services)}/{len(deployment.target_services)}"
        )

        if "overall_metrics" in results:
            metrics = results["overall_metrics"].get("aggregate_metrics", {})
            if metrics:
                print(
                    f"Overall Hit Rate: {metrics.get('overall_hit_rate_percent', 0)}%"
                )
                print(
                    f"Target Met: {'✅' if metrics.get('target_met', False) else '❌'}"
                )

        print("\n📋 Service Details:")
        for service_name, service_result in results["services"].items():
            status_icon = "✅" if service_result["status"] == "success" else "❌"
            print(f"  {status_icon} {service_name}: {service_result['status']}")

        # Exit code based on deployment status
        if results["overall_status"] == "success":
            print("\n🎉 Cache optimization deployment completed successfully!")
            return 0
        elif results["overall_status"] == "partial_success":
            print("\n⚠️ Cache optimization partially deployed. Check logs for details.")
            return 1
        else:
            print("\n❌ Cache optimization deployment failed. Check logs for details.")
            return 2

    except Exception as e:
        logger.error(f"Deployment script error: {e}")
        print(f"\n💥 Deployment script failed: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
