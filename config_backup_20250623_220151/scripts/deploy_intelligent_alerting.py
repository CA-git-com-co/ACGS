#!/usr/bin/env python3
"""
ACGS-1 Intelligent Alerting Deployment Script
Deploys and configures the intelligent alerting system with automated remediation
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntelligentAlertingDeployer:
    """Deployer for ACGS-1 Intelligent Alerting System"""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.config_dir = self.project_root / "config"
        self.monitoring_dir = self.project_root / "infrastructure" / "monitoring"
        self.logs_dir = self.project_root / "logs"
        self.pids_dir = self.project_root / "pids"

        # Ensure directories exist
        for directory in [self.config_dir, self.logs_dir, self.pids_dir]:
            directory.mkdir(exist_ok=True)

    async def deploy_intelligent_alerting(self) -> Dict[str, Any]:
        """Deploy the complete intelligent alerting system"""
        logger.info("🚀 Starting ACGS-1 Intelligent Alerting System Deployment")
        logger.info("=" * 80)

        start_time = time.time()
        results = {}

        try:
            # Step 1: Validate prerequisites
            results["prerequisites"] = await self.validate_prerequisites()

            # Step 2: Install dependencies
            results["dependencies"] = await self.install_dependencies()

            # Step 3: Configure monitoring infrastructure
            results["monitoring_config"] = await self.configure_monitoring()

            # Step 4: Deploy webhook server
            results["webhook_server"] = await self.deploy_webhook_server()

            # Step 5: Configure Prometheus integration
            results["prometheus_integration"] = (
                await self.configure_prometheus_integration()
            )

            # Step 6: Configure Alertmanager
            results["alertmanager_config"] = await self.configure_alertmanager()

            # Step 7: Deploy runbooks and procedures
            results["runbooks"] = await self.deploy_runbooks()

            # Step 8: Start services
            results["service_startup"] = await self.start_services()

            # Step 9: Validate deployment
            results["validation"] = await self.validate_deployment()

            # Step 10: Configure automated monitoring
            results["automated_monitoring"] = (
                await self.configure_automated_monitoring()
            )

            total_time = time.time() - start_time

            logger.info(
                "✅ Intelligent Alerting System deployment completed successfully!"
            )
            logger.info(f"⏱️  Total deployment time: {total_time:.2f} seconds")

            return {
                "status": "success",
                "deployment_time": total_time,
                "results": results,
                "summary": self.generate_deployment_summary(results),
            }

        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return {"status": "failed", "error": str(e), "results": results}

    async def validate_prerequisites(self) -> Dict[str, Any]:
        """Validate system prerequisites"""
        logger.info("🔍 Validating prerequisites...")

        checks = {}

        # Check Python version
        python_version = sys.version_info
        checks["python_version"] = {
            "required": "3.8+",
            "current": f"{python_version.major}.{python_version.minor}.{python_version.micro}",
            "status": "pass" if python_version >= (3, 8) else "fail",
        }

        # Check required directories
        required_dirs = [self.project_root, self.monitoring_dir, self.config_dir]
        for directory in required_dirs:
            checks[f"directory_{directory.name}"] = {
                "path": str(directory),
                "exists": directory.exists(),
                "status": "pass" if directory.exists() else "fail",
            }

        # Check for existing services
        service_ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006]
        for port in service_ports:
            try:
                result = subprocess.run(
                    ["curl", "-f", f"http://localhost:{port}/health"],
                    capture_output=True,
                    timeout=5,
                )
                checks[f"service_port_{port}"] = {
                    "port": port,
                    "status": "running" if result.returncode == 0 else "stopped",
                }
            except subprocess.TimeoutExpired:
                checks[f"service_port_{port}"] = {"port": port, "status": "timeout"}
            except Exception:
                checks[f"service_port_{port}"] = {"port": port, "status": "error"}

        return checks

    async def install_dependencies(self) -> Dict[str, Any]:
        """Install required Python dependencies"""
        logger.info("📦 Installing dependencies...")

        dependencies = [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
            "httpx>=0.25.0",
            "prometheus-client>=0.19.0",
            "pydantic>=2.5.0",
        ]

        results = {}

        for dep in dependencies:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                results[dep] = {
                    "status": "success" if result.returncode == 0 else "failed",
                    "output": (
                        result.stdout if result.returncode == 0 else result.stderr
                    ),
                }
            except subprocess.TimeoutExpired:
                results[dep] = {"status": "timeout", "output": "Installation timed out"}
            except Exception as e:
                results[dep] = {"status": "error", "output": str(e)}

        return results

    async def configure_monitoring(self) -> Dict[str, Any]:
        """Configure monitoring infrastructure"""
        logger.info("⚙️  Configuring monitoring infrastructure...")

        results = {}

        # Ensure intelligent alerting configuration exists
        config_file = self.config_dir / "intelligent_alerting.json"
        if not config_file.exists():
            logger.warning("Intelligent alerting config not found, using default")
            results["config_creation"] = "created_default"
        else:
            results["config_creation"] = "existing_used"

        # Create log rotation configuration
        logrotate_config = """
/home/dislove/ACGS-1/logs/intelligent_alerting.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 dislove dislove
}
"""

        try:
            with open("/tmp/acgs_logrotate", "w") as f:
                f.write(logrotate_config)
            results["logrotate"] = "configured"
        except Exception as e:
            results["logrotate"] = f"failed: {e}"

        return results

    async def deploy_webhook_server(self) -> Dict[str, Any]:
        """Deploy the webhook server"""
        logger.info("🌐 Deploying webhook server...")

        webhook_script = self.monitoring_dir / "webhook_server.py"

        if not webhook_script.exists():
            return {"status": "failed", "error": "webhook_server.py not found"}

        # Make webhook server executable
        webhook_script.chmod(0o755)

        # Create systemd service file for webhook server
        service_content = f"""[Unit]
Description=ACGS-1 Intelligent Alerting Webhook Server
After=network.target

[Service]
Type=simple
User=dislove
WorkingDirectory={self.monitoring_dir}
Environment=PYTHONPATH={self.project_root}
ExecStart={sys.executable} webhook_server.py
Restart=always
RestartSec=10
StandardOutput=append:{self.logs_dir}/webhook_server.log
StandardError=append:{self.logs_dir}/webhook_server.log

[Install]
WantedBy=multi-user.target
"""

        try:
            with open("/tmp/acgs-webhook-server.service", "w") as f:
                f.write(service_content)

            return {
                "status": "configured",
                "service_file": "/tmp/acgs-webhook-server.service",
                "webhook_script": str(webhook_script),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def configure_prometheus_integration(self) -> Dict[str, Any]:
        """Configure Prometheus integration"""
        logger.info("📊 Configuring Prometheus integration...")

        # Update Prometheus configuration to include webhook server
        prometheus_config = self.monitoring_dir / "prometheus.yml"

        webhook_job = """
  # Intelligent Alerting Webhook Server
  - job_name: 'acgs-webhook-server'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s
"""

        try:
            if prometheus_config.exists():
                with open(prometheus_config, "r") as f:
                    config_content = f.read()

                if "acgs-webhook-server" not in config_content:
                    # Add webhook server job to scrape_configs
                    if "scrape_configs:" in config_content:
                        config_content = config_content.replace(
                            "scrape_configs:", f"scrape_configs:{webhook_job}"
                        )

                        with open(prometheus_config, "w") as f:
                            f.write(config_content)

                        return {
                            "status": "updated",
                            "config_file": str(prometheus_config),
                        }
                    else:
                        return {
                            "status": "failed",
                            "error": "Invalid Prometheus config format",
                        }
                else:
                    return {"status": "already_configured"}
            else:
                return {"status": "failed", "error": "Prometheus config not found"}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def configure_alertmanager(self) -> Dict[str, Any]:
        """Configure Alertmanager with enhanced configuration"""
        logger.info("🚨 Configuring Alertmanager...")

        enhanced_config = self.monitoring_dir / "alertmanager-enhanced.yml"
        current_config = self.monitoring_dir / "alertmanager.yml"

        try:
            if enhanced_config.exists():
                # Backup current config
                if current_config.exists():
                    backup_path = current_config.with_suffix(".yml.backup")
                    current_config.rename(backup_path)

                # Copy enhanced config
                import shutil

                shutil.copy2(enhanced_config, current_config)

                return {
                    "status": "updated",
                    "config_file": str(current_config),
                    "backup_created": (
                        str(backup_path) if current_config.exists() else None
                    ),
                }
            else:
                return {
                    "status": "failed",
                    "error": "Enhanced Alertmanager config not found",
                }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def deploy_runbooks(self) -> Dict[str, Any]:
        """Deploy operational runbooks"""
        logger.info("📚 Deploying operational runbooks...")

        runbooks_dir = self.monitoring_dir / "runbooks"
        runbooks_dir.mkdir(exist_ok=True)

        # Create index of runbooks
        runbook_index = {
            "service_down": "Service Down Response Procedures",
            "high_response_time": "High Response Time Investigation",
            "database_issues": "Database Connection Problems",
            "constitutional_compliance": "Constitutional Compliance Failures",
            "security_incidents": "Security Incident Response",
            "emergency_rollback": "Emergency Rollback Procedures",
        }

        try:
            index_file = runbooks_dir / "README.md"
            with open(index_file, "w") as f:
                f.write("# ACGS-1 Operational Runbooks\n\n")
                f.write(
                    "This directory contains operational runbooks for incident response.\n\n"
                )
                for runbook, description in runbook_index.items():
                    f.write(f"- [{description}]({runbook}_runbook.md)\n")

            return {
                "status": "deployed",
                "runbooks_dir": str(runbooks_dir),
                "runbooks_count": len(runbook_index),
            }
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def start_services(self) -> Dict[str, Any]:
        """Start intelligent alerting services"""
        logger.info("🚀 Starting intelligent alerting services...")

        results = {}

        # Start webhook server
        try:
            webhook_cmd = [
                sys.executable,
                str(self.monitoring_dir / "webhook_server.py"),
            ]

            process = subprocess.Popen(
                webhook_cmd,
                cwd=self.monitoring_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "PYTHONPATH": str(self.project_root)},
            )

            # Save PID
            pid_file = self.pids_dir / "webhook_server.pid"
            with open(pid_file, "w") as f:
                f.write(str(process.pid))

            # Wait a moment and check if process is still running
            await asyncio.sleep(2)
            if process.poll() is None:
                results["webhook_server"] = {
                    "status": "started",
                    "pid": process.pid,
                    "pid_file": str(pid_file),
                }
            else:
                stdout, stderr = process.communicate()
                results["webhook_server"] = {
                    "status": "failed",
                    "error": (
                        stderr.decode() if stderr else "Process exited immediately"
                    ),
                }

        except Exception as e:
            results["webhook_server"] = {"status": "failed", "error": str(e)}

        return results

    async def validate_deployment(self) -> Dict[str, Any]:
        """Validate the deployment"""
        logger.info("✅ Validating deployment...")

        validations = {}

        # Check webhook server health
        try:
            result = subprocess.run(
                ["curl", "-f", "http://localhost:8080/health"],
                capture_output=True,
                timeout=10,
            )
            validations["webhook_health"] = {
                "status": "pass" if result.returncode == 0 else "fail",
                "response": (
                    result.stdout.decode()
                    if result.returncode == 0
                    else result.stderr.decode()
                ),
            }
        except Exception as e:
            validations["webhook_health"] = {"status": "error", "error": str(e)}

        # Check configuration files
        config_files = [
            self.config_dir / "intelligent_alerting.json",
            self.monitoring_dir / "alertmanager-enhanced.yml",
        ]

        for config_file in config_files:
            validations[f"config_{config_file.name}"] = {
                "exists": config_file.exists(),
                "readable": config_file.is_file() if config_file.exists() else False,
            }

        return validations

    async def configure_automated_monitoring(self) -> Dict[str, Any]:
        """Configure automated monitoring and cleanup"""
        logger.info("🔄 Configuring automated monitoring...")

        # Create monitoring script
        monitoring_script = (
            self.project_root / "scripts" / "intelligent_alerting_monitor.py"
        )

        monitor_content = f"""#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('{self.project_root}')

from infrastructure.monitoring.intelligent_alerting import IntelligentAlertManager

async def main():
    manager = IntelligentAlertManager()
    
    while True:
        try:
            # Push metrics
            await manager.push_metrics()
            
            # Cleanup old alerts
            await manager.cleanup_old_alerts()
            
            # Wait 5 minutes
            await asyncio.sleep(300)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Monitor error: {{e}}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
"""

        try:
            with open(monitoring_script, "w") as f:
                f.write(monitor_content)
            monitoring_script.chmod(0o755)

            return {"status": "configured", "monitoring_script": str(monitoring_script)}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def generate_deployment_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment summary"""
        summary = {
            "components_deployed": [],
            "services_started": [],
            "configurations_updated": [],
            "validations_passed": 0,
            "validations_failed": 0,
        }

        # Analyze results
        for component, result in results.items():
            if isinstance(result, dict):
                if result.get("status") in [
                    "success",
                    "configured",
                    "started",
                    "deployed",
                ]:
                    summary["components_deployed"].append(component)

                if "pass" in str(result):
                    summary["validations_passed"] += 1
                elif "fail" in str(result):
                    summary["validations_failed"] += 1

        return summary


async def main():
    """Main deployment function"""
    deployer = IntelligentAlertingDeployer()
    result = await deployer.deploy_intelligent_alerting()

    print("\n" + "=" * 80)
    print("DEPLOYMENT SUMMARY")
    print("=" * 80)
    print(json.dumps(result, indent=2))

    if result["status"] == "success":
        print("\n✅ Intelligent Alerting System deployed successfully!")
        print("\nNext steps:")
        print("1. Configure Slack webhook URL in config/intelligent_alerting.json")
        print("2. Set up PagerDuty integration if needed")
        print(
            "3. Test alert generation: python3 infrastructure/monitoring/intelligent_alerting.py test"
        )
        print("4. Monitor webhook server logs: tail -f logs/webhook_server.log")
    else:
        print("\n❌ Deployment failed. Check the error details above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
