#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Deploy Monitoring Infrastructure for ACGS Repositories

This script deploys the monitoring stack for each repository.
"""

import logging
import os
import subprocess
import time
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MonitoringDeployment:
    def __init__(self, workspace_path: Path):
        self.workspace_path = Path(workspace_path)
        self.repositories = [
            "acgs-core",
            "acgs-platform",
            "acgs-blockchain",
            "acgs-models",
            "acgs-applications",
            "acgs-infrastructure",
            "acgs-tools",
        ]

    def check_docker_available(self) -> bool:
        """Check if Docker is available and running"""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True)
            return result.returncode == 0
        except FileNotFoundError:
            logger.error("Docker not found. Please install Docker.")
            return False

    def deploy_monitoring_stack(self, repo_name: str, detached: bool = True) -> bool:
        """Deploy monitoring stack for a repository"""
        try:
            repo_path = self.workspace_path / repo_name
            monitoring_path = repo_path / "monitoring"

            if not monitoring_path.exists():
                logger.error(f"Monitoring directory not found for {repo_name}")
                return False

            logger.info(f"Deploying monitoring stack for {repo_name}...")

            # Change to monitoring directory
            original_dir = os.getcwd()
            os.chdir(monitoring_path)

            # Deploy with Docker Compose
            compose_cmd = [
                "docker",
                "compose",
                "-f",
                "docker-compose.monitoring.yml",
                "up",
            ]

            if detached:
                compose_cmd.append("-d")

            result = subprocess.run(compose_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ Monitoring stack deployed for {repo_name}")
                return True
            else:
                logger.error(
                    f"❌ Failed to deploy monitoring for {repo_name}: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Exception deploying monitoring for {repo_name}: {e}")
            return False
        finally:
            os.chdir(original_dir)

    def check_monitoring_health(self, repo_name: str, port_offset: int = 0) -> dict:
        """Check if monitoring services are healthy"""
        base_ports = {"prometheus": 9090, "grafana": 3000, "alertmanager": 9093}

        health_status = {}

        for service, base_port in base_ports.items():
            port = base_port + port_offset
            try:
                response = requests.get(f"http://localhost:{port}", timeout=5)
                health_status[service] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "port": port,
                    "url": f"http://localhost:{port}",
                }
            except requests.exceptions.RequestException:
                health_status[service] = {
                    "status": "unreachable",
                    "port": port,
                    "url": f"http://localhost:{port}",
                }

        return health_status

    def create_monitoring_summary(self, deployments: dict) -> str:
        """Create monitoring deployment summary"""
        successful = [
            repo for repo, status in deployments.items() if status == "success"
        ]
        failed = [repo for repo, status in deployments.items() if status == "failed"]

        summary = f"""# ACGS Monitoring Deployment Summary

## Overview
Deployed monitoring infrastructure for ACGS repositories.

## Successful Deployments ({len(successful)})
"""

        port_mapping = {
            "acgs-core": 0,
            "acgs-platform": 10,
            "acgs-blockchain": 20,
            "acgs-models": 30,
            "acgs-applications": 40,
            "acgs-infrastructure": 50,
            "acgs-tools": 60,
        }

        for repo in successful:
            offset = port_mapping.get(repo, 0)
            prometheus_port = 9090 + offset
            grafana_port = 3000 + offset
            alertmanager_port = 9093 + offset

            summary += f"""
### {repo}
- **Prometheus**: http://localhost:{prometheus_port}
- **Grafana**: http://localhost:{grafana_port} (admin/admin)
- **Alertmanager**: http://localhost:{alertmanager_port}
- **Health Check**: http://localhost:800{1 + list(self.repositories).index(repo)}/health
"""

        if failed:
            summary += f"\n## Failed Deployments ({len(failed)})\n"
            for repo in failed:
                summary += f"- ❌ **{repo}**: Deployment failed\n"

        summary += f"""
## Access Instructions

### Grafana Dashboards
1. Open Grafana at the URLs above
2. Login with admin/admin
3. Navigate to Dashboards → Browse
4. Select the {repo} dashboard

### Prometheus Metrics
1. Open Prometheus at the URLs above
2. Navigate to Status → Targets to verify scraping
3. Use the query interface to explore metrics

### Alertmanager
1. Open Alertmanager at the URLs above
2. View active alerts and routing configuration
3. Configure notification channels as needed

## Health Monitoring

Each service exposes health endpoints:
```bash
# Basic health check
curl http://localhost:800X/health

# Detailed metrics
curl http://localhost:800X/health/detailed

# Prometheus metrics
curl http://localhost:800X/metrics
```

## Management Commands

### Start monitoring stack
```bash
cd /home/dislove/acgs-workspace/[repository]/monitoring
docker compose -f docker-compose.monitoring.yml up -d
```

### Stop monitoring stack
```bash
cd /home/dislove/acgs-workspace/[repository]/monitoring  
docker compose -f docker-compose.monitoring.yml down
```

### View logs
```bash
docker compose -f docker-compose.monitoring.yml logs -f
```

## Next Steps

1. **Configure Alerting**: Update Slack webhooks and email settings
2. **Customize Dashboards**: Add repository-specific metrics
3. **Set Up Log Aggregation**: Integrate with ELK stack
4. **Configure Backup**: Set up monitoring data backup
5. **Team Training**: Train teams on monitoring tools

## Support

- **Grafana Documentation**: https://grafana.com/docs/
- **Prometheus Documentation**: https://prometheus.io/docs/
- **Alertmanager Documentation**: https://prometheus.io/docs/alerting/alertmanager/
"""

        return summary

    def deploy_test_monitoring(self, repo_name: str = "acgs-core") -> bool:
        """Deploy monitoring for one repository as a test"""
        logger.info(f"Deploying test monitoring stack for {repo_name}...")

        if not self.check_docker_available():
            return False

        success = self.deploy_monitoring_stack(repo_name)

        if success:
            logger.info("Waiting for services to start...")
            time.sleep(10)

            health = self.check_monitoring_health(repo_name)
            logger.info(f"Health check results for {repo_name}:")
            for service, status in health.items():
                logger.info(f"  {service}: {status['status']} at {status['url']}")

        return success

    def deploy_all_monitoring(self, test_mode: bool = False) -> dict:
        """Deploy monitoring for all repositories"""
        if not self.check_docker_available():
            return {"error": "Docker not available"}

        deployments = {}

        # In test mode, only deploy one repository
        repos_to_deploy = [self.repositories[0]] if test_mode else self.repositories

        for repo_name in repos_to_deploy:
            logger.info(f"\n=== Deploying monitoring for {repo_name} ===")

            if self.deploy_monitoring_stack(repo_name):
                deployments[repo_name] = "success"
            else:
                deployments[repo_name] = "failed"

        return deployments


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Deploy monitoring infrastructure for ACGS"
    )
    parser.add_argument("workspace_path", help="Path to ACGS workspace")
    parser.add_argument("--repo", help="Deploy monitoring for specific repository only")
    parser.add_argument(
        "--test", action="store_true", help="Deploy test monitoring (single repo)"
    )
    parser.add_argument(
        "--health-check",
        action="store_true",
        help="Only check health of existing monitoring",
    )

    args = parser.parse_args()

    deployment = MonitoringDeployment(args.workspace_path)

    if args.health_check:
        # Check health of all monitoring stacks
        for i, repo_name in enumerate(deployment.repositories):
            logger.info(f"\nChecking {repo_name} monitoring health...")
            health = deployment.check_monitoring_health(repo_name, port_offset=i * 10)
            for service, status in health.items():
                logger.info(f"  {service}: {status['status']} at {status['url']}")
        return

    if args.repo:
        # Deploy single repository
        success = deployment.deploy_monitoring_stack(args.repo)
        logger.info(
            f"Monitoring deployment for {args.repo}: {'SUCCESS' if success else 'FAILED'}"
        )
    elif args.test:
        # Deploy test monitoring
        success = deployment.deploy_test_monitoring()
        logger.info(f"Test monitoring deployment: {'SUCCESS' if success else 'FAILED'}")
    else:
        # Deploy all monitoring
        results = deployment.deploy_all_monitoring()

        # Generate summary
        summary = deployment.create_monitoring_summary(results)
        summary_file = Path(args.workspace_path) / "MONITORING_DEPLOYMENT_SUMMARY.md"
        with open(summary_file, "w") as f:
            f.write(summary)

        successful = [repo for repo, status in results.items() if status == "success"]
        failed = [repo for repo, status in results.items() if status == "failed"]

        logger.info(f"\nMonitoring deployment complete!")
        logger.info(f"Successful: {len(successful)}/{len(results)}")
        if failed:
            logger.warning(f"Failed: {', '.join(failed)}")
        logger.info(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()
