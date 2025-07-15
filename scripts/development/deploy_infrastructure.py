#!/usr/bin/env python3
"""
ACGS-1 Infrastructure as Code Deployment Script
Orchestrates Terraform and Ansible for complete infrastructure deployment
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfrastructureDeployer:
    """Complete Infrastructure as Code deployment orchestrator"""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.terraform_dir = self.project_root / "infrastructure" / "terraform"
        self.ansible_dir = self.project_root / "infrastructure" / "ansible"
        self.constitutional_hash = "cdd01ef066bc6cf2"

    async def deploy_complete_infrastructure(
        self, environment: str = "development"
    ) -> dict[str, Any]:
        """Deploy complete infrastructure using Terraform and Ansible"""
        logger.info(f"🚀 Starting Complete Infrastructure Deployment for {environment}")
        logger.info("=" * 80)

        start_time = time.time()
        results = {}

        try:
            # Step 1: Validate prerequisites
            results["prerequisites"] = await self.validate_prerequisites()

            # Step 2: Initialize Terraform
            results["terraform_init"] = await self.terraform_init()

            # Step 3: Plan Terraform deployment
            results["terraform_plan"] = await self.terraform_plan(environment)

            # Step 4: Apply Terraform infrastructure
            results["terraform_apply"] = await self.terraform_apply(environment)

            # Step 5: Extract Terraform outputs
            results["terraform_outputs"] = await self.get_terraform_outputs()

            # Step 6: Generate Ansible inventory from Terraform
            results["ansible_inventory"] = await self.generate_ansible_inventory(
                results["terraform_outputs"]
            )

            # Step 7: Run Ansible configuration
            results["ansible_deployment"] = await self.run_ansible_deployment(
                environment
            )

            # Step 8: Validate infrastructure deployment
            results["infrastructure_validation"] = await self.validate_infrastructure()

            # Step 9: Setup monitoring and alerting
            results["monitoring_setup"] = await self.setup_monitoring()

            # Step 10: Generate deployment documentation
            results["documentation"] = await self.generate_deployment_documentation(
                results
            )

            total_time = time.time() - start_time

            logger.info("✅ Complete infrastructure deployment completed successfully!")
            logger.info(f"⏱️  Total deployment time: {total_time:.2f} seconds")

            return {
                "status": "success",
                "environment": environment,
                "deployment_time": total_time,
                "results": results,
                "summary": self.generate_deployment_summary(results),
            }

        except Exception as e:
            logger.error(f"❌ Infrastructure deployment failed: {e}")
            return {"status": "failed", "error": str(e), "results": results}

    async def validate_prerequisites(self) -> dict[str, Any]:
        """Validate deployment prerequisites"""
        logger.info("🔍 Validating prerequisites...")

        validation = {}

        # Check Terraform
        try:
            result = await self.run_command(["terraform", "--version"])
            validation["terraform"] = {
                "available": result["returncode"] == 0,
                "version": (
                    result["stdout"][:100] if result["returncode"] == 0 else None
                ),
            }
        except Exception as e:
            validation["terraform"] = {"available": False, "error": str(e)}

        # Check Ansible
        try:
            result = await self.run_command(["ansible", "--version"])
            validation["ansible"] = {
                "available": result["returncode"] == 0,
                "version": (
                    result["stdout"][:100] if result["returncode"] == 0 else None
                ),
            }
        except Exception as e:
            validation["ansible"] = {"available": False, "error": str(e)}

        # Check AWS CLI
        try:
            result = await self.run_command(["aws", "--version"])
            validation["aws_cli"] = {
                "available": result["returncode"] == 0,
                "version": (
                    result["stdout"][:100] if result["returncode"] == 0 else None
                ),
            }
        except Exception as e:
            validation["aws_cli"] = {"available": False, "error": str(e)}

        # Check kubectl
        try:
            result = await self.run_command(["kubectl", "version", "--client"])
            validation["kubectl"] = {
                "available": result["returncode"] == 0,
                "version": (
                    result["stdout"][:100] if result["returncode"] == 0 else None
                ),
            }
        except Exception as e:
            validation["kubectl"] = {"available": False, "error": str(e)}

        # Check required directories
        validation["directories"] = {
            "terraform_dir": self.terraform_dir.exists(),
            "ansible_dir": self.ansible_dir.exists(),
            "project_root": self.project_root.exists(),
        }

        return validation

    async def terraform_init(self) -> dict[str, Any]:
        """Initialize Terraform"""
        logger.info("🏗️ Initializing Terraform...")

        try:
            result = await self.run_command(
                ["terraform", "init", "-upgrade"], cwd=self.terraform_dir
            )

            return {
                "status": "success" if result["returncode"] == 0 else "failed",
                "output": (
                    result["stdout"] if result["returncode"] == 0 else result["stderr"]
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def terraform_plan(self, environment: str) -> dict[str, Any]:
        """Plan Terraform deployment"""
        logger.info(f"📋 Planning Terraform deployment for {environment}...")

        try:
            # Create terraform.tfvars for environment
            await self.create_terraform_vars(environment)

            result = await self.run_command(
                [
                    "terraform",
                    "plan",
                    f"-var-file=environments/{environment}.tfvars",
                    f"-out=tfplan-{environment}",
                ],
                cwd=self.terraform_dir,
            )

            return {
                "status": "success" if result["returncode"] == 0 else "failed",
                "output": (
                    result["stdout"] if result["returncode"] == 0 else result["stderr"]
                ),
                "plan_file": f"tfplan-{environment}",
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def terraform_apply(self, environment: str) -> dict[str, Any]:
        """Apply Terraform infrastructure"""
        logger.info(f"🚀 Applying Terraform infrastructure for {environment}...")

        try:
            result = await self.run_command(
                ["terraform", "apply", f"tfplan-{environment}", "-auto-approve"],
                cwd=self.terraform_dir,
            )

            return {
                "status": "success" if result["returncode"] == 0 else "failed",
                "output": (
                    result["stdout"] if result["returncode"] == 0 else result["stderr"]
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_terraform_outputs(self) -> dict[str, Any]:
        """Get Terraform outputs"""
        logger.info("📤 Extracting Terraform outputs...")

        try:
            result = await self.run_command(
                ["terraform", "output", "-json"], cwd=self.terraform_dir
            )

            if result["returncode"] == 0:
                outputs = json.loads(result["stdout"])
                return {"status": "success", "outputs": outputs}
            return {"status": "failed", "error": result["stderr"]}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def generate_ansible_inventory(
        self, terraform_outputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate Ansible inventory from Terraform outputs"""
        logger.info("📝 Generating Ansible inventory...")

        try:
            if terraform_outputs.get("status") != "success":
                return {
                    "status": "skipped",
                    "reason": "Terraform outputs not available",
                }

            outputs = terraform_outputs.get("outputs", {})

            # Generate dynamic inventory
            inventory = {
                "all": {
                    "vars": {
                        "constitutional_hash": self.constitutional_hash,
                        "cluster_name": outputs.get("cluster_name", {}).get(
                            "value", ""
                        ),
                        "cluster_endpoint": outputs.get("cluster_endpoint", {}).get(
                            "value", ""
                        ),
                        "database_endpoint": outputs.get("database_endpoint", {}).get(
                            "value", ""
                        ),
                        "redis_endpoint": outputs.get("redis_endpoint", {}).get(
                            "value", ""
                        ),
                    }
                },
                "_meta": {"hostvars": {}},
            }

            # Save inventory
            inventory_file = self.ansible_dir / "inventory" / "dynamic.json"
            inventory_file.parent.mkdir(parents=True, exist_ok=True)

            with open(inventory_file, "w") as f:
                json.dump(inventory, f, indent=2)

            return {
                "status": "success",
                "inventory_file": str(inventory_file),
                "inventory": inventory,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def run_ansible_deployment(self, environment: str) -> dict[str, Any]:
        """Run Ansible deployment"""
        logger.info(f"⚙️ Running Ansible deployment for {environment}...")

        try:
            # Run main site playbook
            result = await self.run_command(
                [
                    "ansible-playbook",
                    "-i",
                    f"inventory/{environment}.yml",
                    "playbooks/site.yml",
                    "--extra-vars",
                    f"environment={environment}",
                    "--extra-vars",
                    f"constitutional_hash={self.constitutional_hash}",
                    "-v",
                ],
                cwd=self.ansible_dir,
            )

            return {
                "status": "success" if result["returncode"] == 0 else "failed",
                "output": (
                    result["stdout"] if result["returncode"] == 0 else result["stderr"]
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def validate_infrastructure(self) -> dict[str, Any]:
        """Validate deployed infrastructure"""
        logger.info("✅ Validating infrastructure deployment...")

        validation_results = {}

        # Validate Kubernetes cluster
        try:
            result = await self.run_command(["kubectl", "cluster-info"])
            validation_results["kubernetes_cluster"] = {
                "status": "healthy" if result["returncode"] == 0 else "unhealthy",
                "info": (
                    result["stdout"][:200]
                    if result["returncode"] == 0
                    else result["stderr"][:200]
                ),
            }
        except Exception as e:
            validation_results["kubernetes_cluster"] = {
                "status": "error",
                "error": str(e),
            }

        # Validate ACGS services
        services = ["auth", "ac", "pgc"]
        for service in services:
            try:
                result = await self.run_command(
                    [
                        "kubectl",
                        "get",
                        "pods",
                        "-n",
                        "acgs-blue",
                        "-l",
                        f"app=acgs-{service}-service",
                        "-o",
                        "jsonpath={.items[*].status.phase}",
                    ]
                )

                phases = result["stdout"].split() if result["returncode"] == 0 else []
                validation_results[f"{service}_service"] = {
                    "status": (
                        "healthy"
                        if all(phase == "Running" for phase in phases)
                        else "unhealthy"
                    ),
                    "pod_count": len(phases),
                }
            except Exception as e:
                validation_results[f"{service}_service"] = {
                    "status": "error",
                    "error": str(e),
                }

        # Validate constitutional compliance
        try:
            result = await self.run_command(
                [
                    "kubectl",
                    "exec",
                    "-n",
                    "acgs-blue",
                    "deployment/acgs-pgc-service-blue",
                    "--",
                    "curl",
                    "-f",
                    "http://localhost:8005/api/v1/governance/compliance/status",  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
                ]
            )

            if result["returncode"] == 0:
                compliance_data = json.loads(result["stdout"])
                validation_results["constitutional_compliance"] = {
                    "status": (
                        "valid"
                        if compliance_data.get("compliance_rate", 0) >= 0.95
                        else "invalid"
                    ),
                    "compliance_rate": compliance_data.get("compliance_rate", 0),
                    "constitutional_hash": compliance_data.get(
                        "constitutional_hash", ""
                    ),
                }
            else:
                validation_results["constitutional_compliance"] = {
                    "status": "error",
                    "error": result["stderr"],
                }
        except Exception as e:
            validation_results["constitutional_compliance"] = {
                "status": "error",
                "error": str(e),
            }

        return validation_results

    async def setup_monitoring(self) -> dict[str, Any]:
        """Setup monitoring and alerting"""
        logger.info("📊 Setting up monitoring and alerting...")

        try:
            # Deploy monitoring stack
            result = await self.run_command(
                [
                    "python3",
                    str(
                        self.project_root / "scripts" / "deploy_intelligent_alerting.py"
                    ),
                ]
            )

            return {
                "status": "success" if result["returncode"] == 0 else "failed",
                "output": (
                    result["stdout"][:200]
                    if result["returncode"] == 0
                    else result["stderr"][:200]
                ),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def create_terraform_vars(self, environment: str) -> None:
        """Create Terraform variables file for environment"""
        vars_dir = self.terraform_dir / "environments"
        vars_dir.mkdir(exist_ok=True)

        vars_content = f"""# ACGS-1 Terraform Variables - {environment.title()}

environment = "{environment}"
aws_region = "us-west-2"
constitutional_hash = "{self.constitutional_hash}"

# Network configuration
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-west-2a", "us-west-2b", "us-west-2c"]

# Kubernetes configuration
kubernetes_version = "1.28"

# Database configuration
db_instance_class = "{"db.r6g.xlarge" if environment == "production" else "db.t3.medium"}"
db_allocated_storage = {500 if environment == "production" else 100}
db_backup_retention_period = {30 if environment == "production" else 7}
db_multi_az = {"true" if environment == "production" else "false"}

# Redis configuration
redis_node_type = "{"cache.r6g.large" if environment == "production" else "cache.t3.micro"}"
redis_num_cache_nodes = {3 if environment == "production" else 1}

# Security configuration
enable_waf = {"true" if environment == "production" else "false"}
enable_guardduty = true
enable_config = true
enable_cloudtrail = true

# Performance configuration
performance_targets = {{
  response_time_ms     = 500
  availability_percent = 99.9
  concurrent_users     = {1000 if environment == "production" else 100}
  throughput_rps      = {100 if environment == "production" else 10}
}}

# Constitutional governance configuration
governance_config = {{
  compliance_threshold    = 0.95
  validation_enabled     = true
  audit_trail_enabled    = true
  stakeholder_notifications = true
}}
"""

        with open(vars_dir / f"{environment}.tfvars", "w") as f:
            f.write(vars_content)

    async def generate_deployment_documentation(
        self, results: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate deployment documentation"""
        logger.info("📚 Generating deployment documentation...")

        docs_dir = self.project_root / "docs" / "infrastructure"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Create deployment report
        deployment_report = {
            "deployment_timestamp": time.time(),
            "constitutional_hash": self.constitutional_hash,
            "infrastructure_components": {
                "terraform": results.get("terraform_apply", {}).get("status"),
                "ansible": results.get("ansible_deployment", {}).get("status"),
                "kubernetes": results.get("infrastructure_validation", {})
                .get("kubernetes_cluster", {})
                .get("status"),
                "monitoring": results.get("monitoring_setup", {}).get("status"),
            },
            "validation_results": results.get("infrastructure_validation", {}),
            "terraform_outputs": results.get("terraform_outputs", {}).get(
                "outputs", {}
            ),
            "deployment_summary": results.get("summary", {}),
        }

        try:
            with open(docs_dir / "deployment_report.json", "w") as f:
                json.dump(deployment_report, f, indent=2)

            return {
                "status": "success",
                "report_file": str(docs_dir / "deployment_report.json"),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def run_command(self, cmd: list[str], cwd: Path = None) -> dict[str, Any]:
        """Run shell command"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.project_root,
            )

            stdout, stderr = await process.communicate()

            return {
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
            }
        except Exception as e:
            return {"returncode": -1, "stdout": "", "stderr": str(e)}

    def generate_deployment_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate deployment summary"""
        summary = {
            "components_deployed": 0,
            "validations_passed": 0,
            "infrastructure_healthy": False,
            "constitutional_compliance": "unknown",
        }

        # Analyze results
        for component, result in results.items():
            if isinstance(result, dict):
                if result.get("status") == "success":
                    summary["components_deployed"] += 1
                    summary["validations_passed"] += 1

        # Check infrastructure health
        validation = results.get("infrastructure_validation", {})
        if validation.get("kubernetes_cluster", {}).get("status") == "healthy":
            summary["infrastructure_healthy"] = True

        # Check constitutional compliance
        compliance = validation.get("constitutional_compliance", {})
        if compliance.get("status") == "valid":
            summary["constitutional_compliance"] = "valid"
        elif compliance.get("status") == "invalid":
            summary["constitutional_compliance"] = "invalid"

        return summary


async def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS-1 Infrastructure as Code Deployment"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default="development",
        help="Target environment",
    )
    parser.add_argument(
        "--terraform-only", action="store_true", help="Run only Terraform deployment"
    )
    parser.add_argument(
        "--ansible-only", action="store_true", help="Run only Ansible configuration"
    )

    args = parser.parse_args()

    deployer = InfrastructureDeployer()

    try:
        result = await deployer.deploy_complete_infrastructure(argsconfig/environments/development.environment)

        print("\n" + "=" * 80)
        print("INFRASTRUCTURE DEPLOYMENT SUMMARY")
        print("=" * 80)
        print(json.dumps(result, indent=2))

        if result["status"] == "success":
            print(
                f"\n✅ Infrastructure deployment for {argsconfig/environments/development.environment} completed successfully!"
            )
            print("\nNext steps:")
            print("1. Verify cluster: kubectl cluster-info")
            print("2. Check services: kubectl get pods --all-namespaces")
            print(
                "3. Test constitutional compliance: curl http://localhost:8005/api/v1/governance/compliance/status"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
            )
        else:
            print(f"\n❌ Infrastructure deployment for {argsconfig/environments/development.environment} failed.")

    except Exception as e:
        logger.error(f"Deployment error: {e}")
        print(f"\n❌ Deployment failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
