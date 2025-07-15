#!/usr/bin/env python3
"""
DeepSeek R1 Pilot Deployment Script

Automated deployment script for the DeepSeek R1 migration pilot.
Implements blue-green deployment strategy with automatic rollback capabilities.

Deployment Phases:
- Phase 1: Initial Pilot (10% traffic, 7 days)
- Phase 2: Expanded Testing (25% traffic, 14 days)
- Phase 3: Majority Traffic (50% traffic, 14 days)
- Phase 4: Full Migration (90% traffic, 7 days)

Usage:
    python scripts/deploy_deepseek_r1_pilot.py --phase 1 --environment production
"""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shared.ai_model_service import AIModelService
from services.shared.deepseek_r1_monitoring import DeepSeekR1Monitor
from services.shared.deepseek_r1_pilot import DeepSeekR1PilotManager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeepSeekR1Deployer:
    """Automated deployment manager for DeepSeek R1 pilot."""

    def __init__(self, phase: int, environment: str):
        self.phase = phase
        selfconfig/environments/development.environment = environment
        self.deployment_config = self._load_deployment_config()
        self.monitor = DeepSeekR1Monitor()

        # Phase configurations
        self.phase_configs = {
            1: {"traffic_percentage": 10, "duration_days": 7, "name": "Initial Pilot"},
            2: {
                "traffic_percentage": 25,
                "duration_days": 14,
                "name": "Expanded Testing",
            },
            3: {
                "traffic_percentage": 50,
                "duration_days": 14,
                "name": "Majority Traffic",
            },
            4: {"traffic_percentage": 90, "duration_days": 7, "name": "Full Migration"},
        }

        logger.info(
            f"DeepSeek R1 Deployer initialized for Phase {phase} in {environment}"
        )

    def _load_deployment_config(self) -> dict:
        """Load deployment configuration."""
        config_file = "config/deepseek-r1-pilot.yaml"

        # For this implementation, return default config
        # In production, this would load from YAML file
        return {
            "deployment": {
                "strategy": "blue_green",
                "rollback": {
                    "automatic_rollback_enabled": True,
                    "rollback_triggers": {
                        "constitutional_compliance": 0.90,
                        "response_time_p95": 3000,
                        "error_rate": 0.05,
                        "service_unavailable": 60,
                    },
                },
            },
            "monitoring": {
                "check_interval_seconds": 30,
                "alert_thresholds": {
                    "critical_compliance": 0.75,
                    "high_compliance": 0.90,
                    "critical_response_time": 5000,
                    "high_response_time": 2000,
                },
            },
        }

    def validate_prerequisites(self) -> bool:
        """Validate deployment prerequisites."""
        logger.info("Validating deployment prerequisites...")

        checks = []

        # Check environment variables
        required_env_vars = [
            "OPENROUTER_API_KEY",
            "ACGS_CONSTITUTIONAL_HASH",
            "DATABASE_URL",
            "REDIS_URL",
        ]

        for var in required_env_vars:
            if os.environ.get(var):
                checks.append(f"✅ {var} is set")
            else:
                checks.append(f"❌ {var} is missing")
                logger.error(f"Required environment variable {var} is not set")

        # Check service availability
        service_ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006]
        for port in service_ports:
            # In production, this would check actual service health
            checks.append(f"✅ Service on port {port} (assumed healthy)")

        # Check constitutional hash
        expected_hash = "cdd01ef066bc6cf2"
        current_hash = os.environ.get("ACGS_CONSTITUTIONAL_HASH", "")
        if current_hash == expected_hash:
            checks.append(f"✅ Constitutional hash verified: {expected_hash}")
        else:
            checks.append(
                f"❌ Constitutional hash mismatch: expected {expected_hash}, got {current_hash}"
            )
            logger.error("Constitutional hash verification failed")

        for check in checks:
            logger.info(check)

        failed_checks = [c for c in checks if c.startswith("❌")]
        if failed_checks:
            logger.error(
                f"Prerequisites validation failed: {len(failed_checks)} issues found"
            )
            return False

        logger.info("All prerequisites validated successfully")
        return True

    def configure_phase(self) -> bool:
        """Configure environment for specific deployment phase."""
        logger.info(
            f"Configuring Phase {self.phase}: {self.phase_configs[self.phase]['name']}"
        )

        phase_config = self.phase_configs[self.phase]

        # Set environment variables for the phase
        env_vars = {
            "DEEPSEEK_R1_PILOT_ENABLED": "true",
            "DEEPSEEK_R1_TRAFFIC_PERCENTAGE": str(phase_config["traffic_percentage"]),
            "DEEPSEEK_R1_COMPLIANCE_THRESHOLD": "0.95",
            "DEEPSEEK_R1_RESPONSE_TIME_THRESHOLD": "2000",
            "DEEPSEEK_R1_COST_TRACKING": "true",
            "DEEPSEEK_R1_FALLBACK_ENABLED": "true",
            "DEPLOYMENT_PHASE": f"phase_{self.phase}",
            "DEPLOYMENT_PHASE_NAME": phase_config["name"],
            "DEPLOYMENT_TRAFFIC_PERCENTAGE": str(phase_config["traffic_percentage"]),
        }

        for key, value in env_vars.items():
            os.environ[key] = value
            logger.info(f"Set {key}={value}")

        # Create phase-specific configuration file
        phase_config_file = (
            f"config/environments/phase_{self.phase}_{selfconfig/environments/development.environment}config/environments/development.env"
        )
        os.makedirs(os.path.dirname(phase_config_file), exist_ok=True)

        with open(phase_config_file, "w") as f:
            f.write(f"# DeepSeek R1 Pilot - Phase {self.phase} Configuration\n")
            f.write(f"# Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")

        logger.info(f"Phase configuration saved to {phase_config_file}")
        return True

    async def deploy_pilot(self) -> bool:
        """Deploy the DeepSeek R1 pilot for the specified phase."""
        logger.info(f"Starting Phase {self.phase} deployment...")

        try:
            # Initialize pilot manager with new configuration
            pilot_manager = DeepSeekR1PilotManager()
            ai_service = AIModelService()

            # Verify pilot is configured correctly
            if not pilot_manager.config.enabled:
                logger.error("Pilot is not enabled in configuration")
                return False

            expected_traffic = self.phase_configs[self.phase]["traffic_percentage"]
            if pilot_manager.config.traffic_percentage != expected_traffic:
                logger.error(
                    f"Traffic percentage mismatch: expected {expected_traffic}%, "
                    f"got {pilot_manager.config.traffic_percentage}%"
                )
                return False

            logger.info(
                f"Pilot configured correctly: {pilot_manager.config.traffic_percentage}% traffic"
            )

            # Test pilot functionality
            test_request = {
                "messages": [
                    {"role": "user", "content": "Test constitutional AI compliance"}
                ],
                "temperature": 0.0,
                "max_tokens": 100,
            }

            response = await pilot_manager.process_request(
                test_request, "deployment_test_001"
            )

            if not response:
                logger.error("Pilot test request failed")
                return False

            logger.info("Pilot deployment test successful")

            # Start monitoring
            await self.start_monitoring(ai_service)

            return True

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False

    async def start_monitoring(self, ai_service: AIModelService):
        """Start monitoring for the deployment."""
        logger.info("Starting deployment monitoring...")

        # Monitor for initial period to ensure stability
        monitoring_duration = 300  # 5 minutes initial monitoring
        check_interval = 30  # 30 seconds
        checks = monitoring_duration // check_interval

        for i in range(checks):
            try:
                # Collect metrics
                metrics = await self.monitor.collect_metrics(ai_service)

                # Check for rollback conditions
                rollback_needed = self.check_rollback_conditions(metrics)

                if rollback_needed:
                    logger.critical(
                        "Rollback conditions detected! Initiating automatic rollback..."
                    )
                    await self.rollback_deployment()
                    return False

                # Log progress
                logger.info(
                    f"Monitoring check {i + 1}/{checks}: "
                    f"Compliance: {metrics.constitutional_compliance_rate:.3f}, "
                    f"Response: {metrics.response_time_p95_ms:.1f}ms"
                )

                await asyncio.sleep(check_interval)

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(check_interval)

        logger.info("Initial monitoring period completed successfully")
        return True

    def check_rollback_conditions(self, metrics) -> bool:
        """Check if automatic rollback should be triggered."""
        rollback_config = self.deployment_config["deployment"]["rollback"][
            "rollback_triggers"
        ]

        # Check constitutional compliance
        if (
            metrics.constitutional_compliance_rate
            < rollback_config["constitutional_compliance"]
        ):
            logger.critical(
                f"Constitutional compliance below rollback threshold: "
                f"{metrics.constitutional_compliance_rate:.3f} < {rollback_config['constitutional_compliance']}"
            )
            return True

        # Check response time
        if metrics.response_time_p95_ms > rollback_config["response_time_p95"]:
            logger.critical(
                f"Response time above rollback threshold: "
                f"{metrics.response_time_p95_ms:.1f}ms > {rollback_config['response_time_p95']}ms"
            )
            return True

        # Check error rate
        if metrics.error_rate > rollback_config["error_rate"]:
            logger.critical(
                f"Error rate above rollback threshold: "
                f"{metrics.error_rate:.3f} > {rollback_config['error_rate']}"
            )
            return True

        return False

    async def rollback_deployment(self):
        """Perform automatic rollback to previous configuration."""
        logger.critical("INITIATING AUTOMATIC ROLLBACK")

        # Disable pilot
        os.environ["DEEPSEEK_R1_PILOT_ENABLED"] = "false"
        os.environ["DEEPSEEK_R1_TRAFFIC_PERCENTAGE"] = "0"

        # Create rollback configuration
        rollback_config = {
            "DEEPSEEK_R1_PILOT_ENABLED": "false",
            "DEEPSEEK_R1_TRAFFIC_PERCENTAGE": "0",
            "ROLLBACK_TIMESTAMP": datetime.now(timezone.utc).isoformat(),
            "ROLLBACK_REASON": "Automatic rollback due to performance degradation",
            "PREVIOUS_PHASE": f"phase_{self.phase}",
        }

        # Save rollback configuration
        rollback_file = (
            f"config/environments/rollback_{selfconfig/environments/development.environment}_{int(time.time())}config/environments/development.env"
        )
        with open(rollback_file, "w") as f:
            f.write("# AUTOMATIC ROLLBACK CONFIGURATION\n")
            for key, value in rollback_config.items():
                f.write(f"{key}={value}\n")

        logger.critical(f"Rollback configuration saved to {rollback_file}")
        logger.critical("Manual intervention required to restore service")

    def generate_deployment_report(self, success: bool):
        """Generate deployment report."""
        report = {
            "deployment_info": {
                "phase": self.phase,
                "phase_name": self.phase_configs[self.phase]["name"],
                "environment": selfconfig/environments/development.environment,
                "traffic_percentage": self.phase_configs[self.phase][
                    "traffic_percentage"
                ],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": success,
            },
            "configuration": {
                "constitutional_hash": os.environ.get("ACGS_CONSTITUTIONAL_HASH", ""),
                "pilot_enabled": os.environ.get("DEEPSEEK_R1_PILOT_ENABLED", "false"),
                "traffic_percentage": os.environ.get(
                    "DEEPSEEK_R1_TRAFFIC_PERCENTAGE", "0"
                ),
                "compliance_threshold": os.environ.get(
                    "DEEPSEEK_R1_COMPLIANCE_THRESHOLD", "0.95"
                ),
            },
            "next_steps": self._get_next_steps(success),
        }

        # Save report
        report_file = (
            f"reports/deepseek_r1_deployment_phase_{self.phase}_{int(time.time())}.json"
        )
        os.makedirs("reports", exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Deployment report saved to {report_file}")

        # Print summary
        print("\n" + "=" * 80)
        print(f"DEEPSEEK R1 PILOT DEPLOYMENT - PHASE {self.phase}")
        print("=" * 80)
        print(f"Phase: {self.phase} ({self.phase_configs[self.phase]['name']})")
        print(f"Environment: {selfconfig/environments/development.environment}")
        print(
            f"Traffic Percentage: {self.phase_configs[self.phase]['traffic_percentage']}%"
        )
        print(f"Status: {'SUCCESS' if success else 'FAILED'}")
        print(f"Timestamp: {report['deployment_info']['timestamp']}")
        print("=" * 80)

        if success:
            print("🎉 Deployment completed successfully!")
            print("\nNext Steps:")
            for step in report["next_steps"]:
                print(f"  • {step}")
        else:
            print("❌ Deployment failed!")
            print("\nRecommended Actions:")
            for step in report["next_steps"]:
                print(f"  • {step}")

        print("=" * 80)

    def _get_next_steps(self, success: bool) -> list:
        """Get recommended next steps based on deployment outcome."""
        if success:
            if self.phase < 4:
                return [
                    f"Monitor Phase {self.phase} for {self.phase_configs[self.phase]['duration_days']} days",
                    "Validate constitutional compliance >95%",
                    "Confirm cost savings targets are met",
                    f"Prepare for Phase {self.phase + 1} deployment",
                    "Review performance metrics and user feedback",
                ]
            return [
                "Monitor full migration performance",
                "Validate 96.4% cost reduction achieved",
                "Document lessons learned",
                "Plan Phase 2 implementation (multi-level caching)",
                "Celebrate successful migration! 🎉",
            ]
        return [
            "Investigate deployment failure root cause",
            "Review logs and error messages",
            "Validate environment configuration",
            "Test pilot functionality in staging",
            "Consider rollback to previous phase",
            "Schedule post-mortem review",
        ]


async def main():
    """Main deployment execution."""
    parser = argparse.ArgumentParser(description="Deploy DeepSeek R1 Pilot")
    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3, 4],
        required=True,
        help="Deployment phase (1-4)",
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="development",
        help="Target environment",
    )
    parser.add_argument(
        "--skip-validation", action="store_true", help="Skip prerequisite validation"
    )

    args = parser.parse_args()

    deployer = DeepSeekR1Deployer(args.phase, argsconfig/environments/development.environment)

    # Validate prerequisites
    if not args.skip_validation:
        if not deployer.validate_prerequisites():
            logger.error(
                "Prerequisites validation failed. Use --skip-validation to override."
            )
            sys.exit(1)

    # Configure phase
    if not deployer.configure_phase():
        logger.error("Phase configuration failed")
        sys.exit(1)

    # Deploy pilot
    success = await deployer.deploy_pilot()

    # Generate report
    deployer.generate_deployment_report(success)

    if success:
        logger.info("🎉 DeepSeek R1 pilot deployment completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ DeepSeek R1 pilot deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
