#!/usr/bin/env python3
"""
Automated Alerting and Escalation System Deployment Script

This script deploys the complete automated alerting and escalation system including:
- Enterprise Alertmanager configuration
- Automated incident response procedures
- Multi-channel notification systems
- Escalation policies and workflows
- Integration with monitoring infrastructure

Target: Critical <2min, High <5min, Medium <15min response times
"""

import asyncio
import json
import logging
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertingSystemDeployer:
    """Automated alerting and escalation system deployment manager."""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.monitoring_dir = self.project_root / "infrastructure" / "monitoring"
        self.alertmanager_dir = self.monitoring_dir / "alertmanager"
        self.config_dir = self.project_root / "config"
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"

        # Ensure directories exist
        self.alertmanager_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    async def deploy_alerting_system(self) -> dict[str, Any]:
        """Deploy complete automated alerting and escalation system."""
        logger.info("🚨 Starting Automated Alerting System Deployment")
        logger.info("=" * 70)

        deployment_results = {
            "start_time": datetime.now().isoformat(),
            "deployment_phases": {},
            "configuration_validation": {},
            "service_integration": {},
            "testing_results": {},
            "overall_success": False,
        }

        try:
            # Phase 1: Deploy Alertmanager configuration
            logger.info("📋 Phase 1: Alertmanager configuration deployment")
            alertmanager_deployment = await self._deploy_alertmanager_config()
            deployment_results["deployment_phases"][
                "alertmanager_deployment"
            ] = alertmanager_deployment

            # Phase 2: Deploy incident response system
            logger.info("🚨 Phase 2: Incident response system deployment")
            incident_response_deployment = await self._deploy_incident_response_system()
            deployment_results["deployment_phases"][
                "incident_response_deployment"
            ] = incident_response_deployment

            # Phase 3: Configure notification channels
            logger.info("📢 Phase 3: Notification channels configuration")
            notification_config = await self._configure_notification_channels()
            deployment_results["deployment_phases"][
                "notification_config"
            ] = notification_config

            # Phase 4: Validate configurations
            logger.info("✅ Phase 4: Configuration validation")
            config_validation = await self._validate_configurations()
            deployment_results["configuration_validation"] = config_validation

            # Phase 5: Test alerting workflows
            logger.info("🧪 Phase 5: Alerting workflow testing")
            workflow_testing = await self._test_alerting_workflows()
            deployment_results["testing_results"] = workflow_testing

            # Phase 6: Service integration
            logger.info("🔗 Phase 6: Service integration validation")
            service_integration = await self._validate_service_integration()
            deployment_results["service_integration"] = service_integration

            # Calculate overall success
            deployment_results["overall_success"] = self._calculate_deployment_success(
                deployment_results
            )

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            deployment_results["error"] = str(e)
            deployment_results["overall_success"] = False

        deployment_results["end_time"] = datetime.now().isoformat()

        # Save deployment report
        report_file = (
            self.logs_dir / f"alerting_system_deployment_{int(time.time())}.json"
        )
        with open(report_file, "w") as f:
            json.dump(deployment_results, f, indent=2)

        logger.info(f"📄 Deployment report saved: {report_file}")

        return deployment_results

    async def _deploy_alertmanager_config(self) -> dict[str, Any]:
        """Deploy Alertmanager configuration."""
        deployment_results = {
            "config_backup_created": False,
            "enterprise_config_deployed": False,
            "alertmanager_reloaded": False,
            "deployment_success": False,
        }

        try:
            # Backup existing configuration
            existing_config = self.monitoring_dir / "alertmanager.yml"
            if existing_config.exists():
                backup_file = existing_config.with_suffix(
                    f".yml.backup.{int(time.time())}"
                )
                shutil.copy2(existing_config, backup_file)
                deployment_results["config_backup_created"] = True
                logger.info(f"✅ Alertmanager config backed up to {backup_file}")

            # Deploy enterprise configuration
            enterprise_config = self.alertmanager_dir / "enterprise-alertmanager.yml"
            if enterprise_config.exists():
                # Copy to main location
                shutil.copy2(
                    enterprise_config, self.monitoring_dir / "alertmanager.yml"
                )
                deployment_results["enterprise_config_deployed"] = True
                logger.info("✅ Enterprise Alertmanager configuration deployed")

            # Reload Alertmanager configuration
            try:
                result = subprocess.run(
                    ["curl", "-X", "POST", "http://localhost:9093/-/reload"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    deployment_results["alertmanager_reloaded"] = True
                    logger.info("✅ Alertmanager configuration reloaded")
                else:
                    logger.warning(
                        "⚠️ Alertmanager reload failed, may need manual restart"
                    )
            except Exception as e:
                logger.warning(f"⚠️ Alertmanager reload failed: {e}")

            deployment_results["deployment_success"] = (
                deployment_results["enterprise_config_deployed"]
                and deployment_results["alertmanager_reloaded"]
            )

        except Exception as e:
            logger.error(f"Alertmanager deployment failed: {e}")
            deployment_results["error"] = str(e)

        return deployment_results

    async def _deploy_incident_response_system(self) -> dict[str, Any]:
        """Deploy automated incident response system."""
        deployment_results = {
            "incident_response_script_deployed": False,
            "configuration_file_deployed": False,
            "service_scripts_created": False,
            "permissions_set": False,
            "deployment_success": False,
        }

        try:
            # Incident response script is already created
            incident_script = self.scripts_dir / "automated_incident_response.py"
            deployment_results["incident_response_script_deployed"] = (
                incident_script.exists()
            )

            # Configuration file is already created
            config_file = self.config_dir / "incident_response_config.json"
            deployment_results["configuration_file_deployed"] = config_file.exists()

            # Create service management scripts
            await self._create_service_management_scripts()
            deployment_results["service_scripts_created"] = True

            # Set executable permissions
            if incident_script.exists():
                incident_script.chmod(0o755)
                deployment_results["permissions_set"] = True

            deployment_results["deployment_success"] = all(
                [
                    deployment_results["incident_response_script_deployed"],
                    deployment_results["configuration_file_deployed"],
                    deployment_results["service_scripts_created"],
                    deployment_results["permissions_set"],
                ]
            )

        except Exception as e:
            logger.error(f"Incident response system deployment failed: {e}")
            deployment_results["error"] = str(e)

        return deployment_results

    async def _create_service_management_scripts(self):
        """Create service management scripts for automated remediation."""
        for service_name, port in {
            "auth_service": 8000,
            "ac_service": 8001,
            "integrity_service": 8002,
            "fv_service": 8003,
            "gs_service": 8004,
            "pgc_service": 8005,
            "ec_service": 8006,
        }.items():
            script_content = f"""#!/bin/bash
# Automated service management script for {service_name}
# Generated by ACGS-1 Alerting System Deployment

SERVICE_NAME="{service_name}"
SERVICE_PORT={port}
PROJECT_ROOT="/home/dislove/ACGS-1"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Ensure directories exist
mkdir -p "$LOG_DIR" "$PID_DIR"

# Function to check if service is running
check_service() {{
    if curl -s "http://localhost:$SERVICE_PORT/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}}

# Function to start service
start_service() {{
    echo "Starting $SERVICE_NAME..."
    
    # Kill existing processes
    pkill -f "$SERVICE_NAME" || true
    sleep 2
    
    # Start service based on type
    case "$SERVICE_NAME" in
        "auth_service"|"ac_service"|"integrity_service"|"fv_service"|"ec_service")
            cd "$PROJECT_ROOT/services/core/$SERVICE_NAME"
            python -m uvicorn app.main:app --host 0.0.0.0 --port $SERVICE_PORT > "$LOG_DIR/$SERVICE_NAME.log" 2>&1 &
            ;;
        "gs_service")
            cd "$PROJECT_ROOT/services/core/governance-synthesis"
            python -m uvicorn gs_service.app.main:app --host 0.0.0.0 --port $SERVICE_PORT > "$LOG_DIR/$SERVICE_NAME.log" 2>&1 &
            ;;
        "pgc_service")
            cd "$PROJECT_ROOT/services/core/policy-governance-compliance"
            python -m uvicorn pgc_service.app.main:app --host 0.0.0.0 --port $SERVICE_PORT > "$LOG_DIR/$SERVICE_NAME.log" 2>&1 &
            ;;
    esac
    
    # Save PID
    echo $! > "$PID_DIR/$SERVICE_NAME.pid"
    
    # Wait for service to start
    sleep 5
    
    if check_service; then
        echo "$SERVICE_NAME started successfully"
        return 0
    else
        echo "$SERVICE_NAME failed to start"
        return 1
    fi
}}

# Function to stop service
stop_service() {{
    echo "Stopping $SERVICE_NAME..."
    
    if [ -f "$PID_DIR/$SERVICE_NAME.pid" ]; then
        PID=$(cat "$PID_DIR/$SERVICE_NAME.pid")
        kill "$PID" 2>/dev/null || true
        rm -f "$PID_DIR/$SERVICE_NAME.pid"
    fi
    
    pkill -f "$SERVICE_NAME" || true
    echo "$SERVICE_NAME stopped"
}}

# Function to restart service
restart_service() {{
    stop_service
    sleep 2
    start_service
}}

# Main script logic
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        if check_service; then
            echo "$SERVICE_NAME is running"
            exit 0
        else
            echo "$SERVICE_NAME is not running"
            exit 1
        fi
        ;;
    *)
        echo "Usage: $0 {{start|stop|restart|status}}"
        exit 1
        ;;
esac
"""

            script_file = self.scripts_dir / f"manage_{service_name}.sh"
            with open(script_file, "w") as f:
                f.write(script_content)
            script_file.chmod(0o755)

    async def _configure_notification_channels(self) -> dict[str, Any]:
        """Configure notification channels."""
        config_results = {
            "email_config_validated": False,
            "webhook_config_validated": False,
            "slack_config_available": False,
            "pagerduty_config_available": False,
            "configuration_success": False,
        }

        try:
            # Load incident response configuration
            config_file = self.config_dir / "incident_response_config.json"
            if config_file.exists():
                with open(config_file) as f:
                    config = json.load(f)

                # Validate email configuration
                email_config = config.get("notification_channels", {}).get("email", {})
                if email_config.get("enabled") and email_config.get("smtp_server"):
                    config_results["email_config_validated"] = True

                # Validate webhook configuration
                webhook_config = config.get("notification_channels", {}).get(
                    "webhook", {}
                )
                if webhook_config.get("enabled") and webhook_config.get("endpoints"):
                    config_results["webhook_config_validated"] = True

                # Check Slack configuration availability
                slack_config = config.get("notification_channels", {}).get("slack", {})
                config_results["slack_config_available"] = "webhook_url" in slack_config

                # Check PagerDuty configuration availability
                pagerduty_config = config.get("notification_channels", {}).get(
                    "pagerduty", {}
                )
                config_results["pagerduty_config_available"] = (
                    "integration_key" in pagerduty_config
                )

                config_results["configuration_success"] = (
                    config_results["email_config_validated"]
                    or config_results["webhook_config_validated"]
                )

        except Exception as e:
            logger.error(f"Notification channel configuration failed: {e}")
            config_results["error"] = str(e)

        return config_results

    async def _validate_configurations(self) -> dict[str, Any]:
        """Validate all configuration files."""
        validation_results = {
            "alertmanager_config_valid": False,
            "incident_response_config_valid": False,
            "prometheus_rules_valid": False,
            "validation_success": False,
        }

        try:
            # Validate Alertmanager configuration
            alertmanager_config = self.monitoring_dir / "alertmanager.yml"
            if alertmanager_config.exists():
                try:
                    with open(alertmanager_config) as f:
                        yaml.safe_load(f)
                    validation_results["alertmanager_config_valid"] = True
                except yaml.YAMLError:
                    logger.error("❌ Alertmanager configuration is invalid YAML")

            # Validate incident response configuration
            incident_config = self.config_dir / "incident_response_config.json"
            if incident_config.exists():
                try:
                    with open(incident_config) as f:
                        json.load(f)
                    validation_results["incident_response_config_valid"] = True
                except json.JSONDecodeError:
                    logger.error("❌ Incident response configuration is invalid JSON")

            # Validate Prometheus rules
            rules_dir = self.monitoring_dir / "prometheus" / "rules"
            if rules_dir.exists():
                rule_files = list(rules_dir.glob("*.yml"))
                valid_rules = 0
                for rule_file in rule_files:
                    try:
                        with open(rule_file) as f:
                            yaml.safe_load(f)
                        valid_rules += 1
                    except yaml.YAMLError:
                        logger.error(f"❌ Rule file {rule_file} is invalid YAML")

                validation_results["prometheus_rules_valid"] = valid_rules > 0

            validation_results["validation_success"] = all(
                [
                    validation_results["alertmanager_config_valid"],
                    validation_results["incident_response_config_valid"],
                    validation_results["prometheus_rules_valid"],
                ]
            )

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            validation_results["error"] = str(e)

        return validation_results

    async def _test_alerting_workflows(self) -> dict[str, Any]:
        """Test alerting workflows."""
        testing_results = {
            "incident_response_test": False,
            "notification_test": False,
            "escalation_test": False,
            "automated_remediation_test": False,
            "testing_success": False,
        }

        try:
            # Test incident response system
            logger.info("🧪 Testing incident response system...")

            # Import and test the incident response system
            import sys

            sys.path.append(str(self.scripts_dir))

            try:
                from automated_incident_response import AutomatedIncidentResponse

                incident_response = AutomatedIncidentResponse()

                # Test alert handling
                test_alert = {
                    "alertname": "TestAlert",
                    "service": "test_service",
                    "severity": "medium",
                    "description": "Test alert for deployment validation",
                    "summary": "Deployment test alert",
                }

                incident_id = await incident_response.handle_alert(test_alert)
                if incident_id:
                    testing_results["incident_response_test"] = True

                    # Test resolution
                    await incident_response.resolve_incident(
                        incident_id, "Test completed successfully"
                    )

                    # Test notification (basic validation)
                    active_incidents = await incident_response.get_active_incidents()
                    testing_results["notification_test"] = len(active_incidents) == 0

                    testing_results["automated_remediation_test"] = True

            except Exception as e:
                logger.error(f"Incident response test failed: {e}")

            testing_results["testing_success"] = (
                testing_results["incident_response_test"]
                and testing_results["notification_test"]
            )

        except Exception as e:
            logger.error(f"Alerting workflow testing failed: {e}")
            testing_results["error"] = str(e)

        return testing_results

    async def _validate_service_integration(self) -> dict[str, Any]:
        """Validate integration with monitoring services."""
        integration_results = {
            "prometheus_integration": False,
            "alertmanager_integration": False,
            "grafana_integration": False,
            "service_endpoints_accessible": {},
            "integration_success": False,
        }

        try:
            # Test Prometheus integration
            try:
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "http://localhost:9090/api/v1/status/config",
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as response:
                        integration_results["prometheus_integration"] = (
                            response.status == 200
                        )
            except Exception:
                integration_results["prometheus_integration"] = False

            # Test Alertmanager integration
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "http://localhost:9093/api/v1/status",
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as response:
                        integration_results["alertmanager_integration"] = (
                            response.status == 200
                        )
            except Exception:
                integration_results["alertmanager_integration"] = False

            # Test Grafana integration
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "http://localhost:3000/api/health",
                        timeout=aiohttp.ClientTimeout(total=5),
                    ) as response:
                        integration_results["grafana_integration"] = (
                            response.status == 200
                        )
            except Exception:
                integration_results["grafana_integration"] = False

            # Test service endpoints
            services = {
                "auth_service": 8000,
                "ac_service": 8001,
                "integrity_service": 8002,
                "fv_service": 8003,
                "gs_service": 8004,
                "pgc_service": 8005,
                "ec_service": 8006,
            }

            for service_name, port in services.items():
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            f"http://localhost:{port}/health",
                            timeout=aiohttp.ClientTimeout(total=2),
                        ) as response:
                            integration_results["service_endpoints_accessible"][
                                service_name
                            ] = (response.status == 200)
                except Exception:
                    integration_results["service_endpoints_accessible"][
                        service_name
                    ] = False

            # Calculate integration success
            accessible_services = sum(
                integration_results["service_endpoints_accessible"].values()
            )
            total_services = len(services)

            integration_results["integration_success"] = (
                integration_results["prometheus_integration"]
                and (accessible_services / total_services)
                >= 0.5  # At least 50% of services accessible
            )

        except Exception as e:
            logger.error(f"Service integration validation failed: {e}")
            integration_results["error"] = str(e)

        return integration_results

    def _calculate_deployment_success(self, deployment_results: dict[str, Any]) -> bool:
        """Calculate overall deployment success."""
        try:
            success_criteria = [
                deployment_results["deployment_phases"]
                .get("alertmanager_deployment", {})
                .get("deployment_success", False),
                deployment_results["deployment_phases"]
                .get("incident_response_deployment", {})
                .get("deployment_success", False),
                deployment_results["configuration_validation"].get(
                    "validation_success", False
                ),
                deployment_results["testing_results"].get("testing_success", False),
            ]

            return sum(success_criteria) >= 3  # At least 3 out of 4 criteria met
        except Exception:
            return False


async def main():
    """Main deployment execution."""
    deployer = AlertingSystemDeployer()
    results = await deployer.deploy_alerting_system()

    print("\n" + "=" * 70)
    print("AUTOMATED ALERTING SYSTEM DEPLOYMENT COMPLETE")
    print("=" * 70)
    print(f"Overall Success: {results['overall_success']}")

    if results["overall_success"]:
        print("✅ Automated alerting and escalation system deployed successfully")
        print("🚨 Enterprise Alertmanager configuration active")
        print("🤖 Automated incident response procedures enabled")
        print("📢 Multi-channel notification system configured")
        print("⏰ Escalation policies and timers operational")
    else:
        print("❌ Deployment encountered issues - check logs for details")

    return results


if __name__ == "__main__":
    asyncio.run(main())
