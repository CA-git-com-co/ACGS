#!/usr/bin/env python3
"""
ACGS-1 Blue-Green Deployment Automation
Zero-downtime deployment system with constitutional compliance validation
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


class BlueGreenDeployer:
    """ACGS-1 Blue-Green Deployment Manager"""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.k8s_dir = (
            self.project_root / "infrastructure" / "kubernetes" / "blue-green"
        )
        self.constitutional_hash = "cdd01ef066bc6cf2"

        # Deployment configuration
        self.services = [
            {"name": "auth-service", "port": 8000, "health_path": "/health"},
            {"name": "ac-service", "port": 8001, "health_path": "/health"},
            {"name": "pgc-service", "port": 8005, "health_path": "/health"},
        ]

        self.namespaces = {
            "blue": "acgs-blue",
            "green": "acgs-green",
            "shared": "acgs-shared",
        }

    async def deploy_blue_green_system(
        self, target_environment: str = "green", image_tag: str = "latest"
    ) -> dict[str, Any]:
        """Deploy new version to target environment"""
        logger.info(
            f"🚀 Starting Blue-Green Deployment to {target_environment} environment"
        )
        logger.info("=" * 80)

        start_time = time.time()
        results = {}

        try:
            # Step 1: Pre-deployment validation
            results["pre_validation"] = await self.pre_deployment_validation()

            # Step 2: Determine current active environment
            results["current_state"] = await self.get_current_deployment_state()
            current_active = results["current_state"]["active_environment"]

            # Step 3: Deploy to target environment
            results["deployment"] = await self.deploy_to_environment(
                target_environment, image_tag
            )

            # Step 4: Health check target environment
            results["health_check"] = await self.comprehensive_health_check(
                target_environment
            )

            # Step 5: Constitutional compliance validation
            results["compliance_check"] = await self.validate_constitutional_compliance(
                target_environment
            )

            # Step 6: Performance validation
            results["performance_check"] = await self.validate_performance(
                target_environment
            )

            # Step 7: Traffic switch decision
            if self.should_switch_traffic(results):
                results["traffic_switch"] = await self.switch_traffic(
                    current_active, target_environment
                )
            else:
                results["traffic_switch"] = {
                    "status": "skipped",
                    "reason": "Validation failed",
                }

            # Step 8: Post-deployment validation
            results["post_validation"] = await self.post_deployment_validation(
                target_environment
            )

            # Step 9: Cleanup old environment (optional)
            if results["traffic_switch"]["status"] == "success":
                results["cleanup"] = await self.cleanup_old_environment(current_active)

            total_time = time.time() - start_time

            logger.info("✅ Blue-Green deployment completed successfully!")
            logger.info(f"⏱️  Total deployment time: {total_time:.2f} seconds")

            return {
                "status": "success",
                "deployment_time": total_time,
                "target_environment": target_environment,
                "previous_environment": current_active,
                "results": results,
                "summary": self.generate_deployment_summary(results),
            }

        except Exception as e:
            logger.error(f"❌ Blue-Green deployment failed: {e}")

            # Attempt rollback if traffic was switched
            if (
                "traffic_switch" in results
                and results["traffic_switch"]["status"] == "success"
            ):
                logger.info("🔄 Attempting automatic rollback...")
                await self.emergency_rollback(current_active)

            return {"status": "failed", "error": str(e), "results": results}

    async def pre_deployment_validation(self) -> dict[str, Any]:
        """Validate system state before deployment"""
        logger.info("🔍 Performing pre-deployment validation...")

        validation = {}

        # Check Kubernetes cluster connectivity
        try:
            result = await self.run_kubectl_command(["cluster-info"])
            validation["cluster_connectivity"] = {
                "status": "success" if result["returncode"] == 0 else "failed",
                "output": result["stdout"][:200],
            }
        except Exception as e:
            validation["cluster_connectivity"] = {"status": "error", "error": str(e)}

        # Check namespace existence
        for env, namespace in self.namespaces.items():
            try:
                result = await self.run_kubectl_command(["get", "namespace", namespace])
                validation[f"namespace_{env}"] = {
                    "status": "exists" if result["returncode"] == 0 else "missing",
                    "namespace": namespace,
                }
            except Exception as e:
                validation[f"namespace_{env}"] = {"status": "error", "error": str(e)}

        # Check shared resources
        try:
            result = await self.run_kubectl_command(
                [
                    "get",
                    "pods",
                    "-n",
                    self.namespaces["shared"],
                    "-l",
                    "component=database",
                ]
            )
            validation["shared_database"] = {
                "status": "running" if "Running" in result["stdout"] else "not_running"
            }
        except Exception as e:
            validation["shared_database"] = {"status": "error", "error": str(e)}

        return validation

    async def get_current_deployment_state(self) -> dict[str, Any]:
        """Get current active environment and deployment state"""
        logger.info("📊 Checking current deployment state...")

        try:
            # Get active environment from traffic config
            result = await self.run_kubectl_command(
                [
                    "get",
                    "configmap",
                    "acgs-traffic-config",
                    "-n",
                    self.namespaces["shared"],
                    "-o",
                    "jsonpath={.data.active-environment}",
                ]
            )

            active_environment = result["stdout"].strip() or "blue"

            # Get deployment status for both environments
            blue_status = await self.get_environment_status("blue")
            green_status = await self.get_environment_status("green")

            return {
                "active_environment": active_environment,
                "blue_status": blue_status,
                "green_status": green_status,
                "traffic_split": await self.get_traffic_split(),
            }

        except Exception as e:
            logger.error(f"Error getting deployment state: {e}")
            return {"active_environment": "blue", "error": str(e)}  # Default fallback

    async def deploy_to_environment(
        self, environment: str, image_tag: str
    ) -> dict[str, Any]:
        """Deploy services to target environment"""
        logger.info(
            f"🚀 Deploying to {environment} environment with tag {image_tag}..."
        )

        deployment_results = {}
        namespace = self.namespaces[environment]

        try:
            # Update image tags in deployment manifests
            manifest_file = self.k8s_dir / f"{environment}-environment.yaml"

            # Apply the deployment
            result = await self.run_kubectl_command(["apply", "-f", str(manifest_file)])

            deployment_results["manifest_apply"] = {
                "status": "success" if result["returncode"] == 0 else "failed",
                "output": (
                    result["stdout"] if result["returncode"] == 0 else result["stderr"]
                ),
            }

            # Wait for deployments to be ready
            for service in self.services:
                deployment_name = f"acgs-{service['name']}-{environment}"

                logger.info(f"Waiting for {deployment_name} to be ready...")

                result = await self.run_kubectl_command(
                    [
                        "rollout",
                        "status",
                        "deployment",
                        deployment_name,
                        "-n",
                        namespace,
                        "--timeout=300s",
                    ]
                )

                deployment_results[f"{service['name']}_rollout"] = {
                    "status": "success" if result["returncode"] == 0 else "failed",
                    "deployment": deployment_name,
                }

            return deployment_results

        except Exception as e:
            logger.error(f"Error deploying to {environment}: {e}")
            return {"status": "error", "error": str(e)}

    async def comprehensive_health_check(self, environment: str) -> dict[str, Any]:
        """Perform comprehensive health check on environment"""
        logger.info(f"🏥 Performing health check on {environment} environment...")

        health_results = {}
        namespace = self.namespaces[environment]

        # Check pod health
        for service in self.services:
            service_name = f"acgs-{service['name']}-{environment}"

            try:
                # Check pod status
                result = await self.run_kubectl_command(
                    [
                        "get",
                        "pods",
                        "-n",
                        namespace,
                        "-l",
                        f"app=acgs-{service['name']},environment={environment}",
                        "-o",
                        "jsonpath={.items[*].status.phase}",
                    ]
                )

                pod_phases = result["stdout"].split()
                all_running = all(phase == "Running" for phase in pod_phases)

                # Check service endpoint health
                endpoint_health = await self.check_service_endpoint(
                    service_name, namespace, service["port"], service["health_path"]
                )

                health_results[service["name"]] = {
                    "pod_status": "healthy" if all_running else "unhealthy",
                    "pod_count": len(pod_phases),
                    "endpoint_health": endpoint_health,
                    "overall_health": (
                        "healthy"
                        if all_running and endpoint_health["status"] == "healthy"
                        else "unhealthy"
                    ),
                }

            except Exception as e:
                health_results[service["name"]] = {"status": "error", "error": str(e)}

        # Overall environment health
        all_healthy = all(
            result.get("overall_health") == "healthy"
            for result in health_results.values()
            if isinstance(result, dict) and "overall_health" in result
        )

        health_results["overall_environment_health"] = (
            "healthy" if all_healthy else "unhealthy"
        )

        return health_results

    async def validate_constitutional_compliance(
        self, environment: str
    ) -> dict[str, Any]:
        """Validate constitutional compliance in target environment"""
        logger.info(
            f"🏛️ Validating constitutional compliance in {environment} environment..."
        )

        namespace = self.namespaces[environment]
        service_name = f"acgs-pgc-service-{environment}"

        try:
            # Check constitutional hash
            hash_result = await self.check_service_endpoint(
                service_name, namespace, 8005, "/api/v1/constitution/hash"
            )

            # Check compliance status
            compliance_result = await self.check_service_endpoint(
                service_name, namespace, 8005, "/api/v1/governance/compliance/status"
            )

            # Parse compliance data
            compliance_data = {}
            if compliance_result["status"] == "healthy" and compliance_result.get(
                "response"
            ):
                try:
                    compliance_data = json.loads(compliance_result["response"])
                except json.JSONDecodeError:
                    pass

            return {
                "constitutional_hash_check": hash_result,
                "compliance_status_check": compliance_result,
                "compliance_rate": compliance_data.get("compliance_rate", 0),
                "constitutional_hash_valid": hash_result.get("response", "").strip()
                == f'"{self.constitutional_hash}"',
                "compliance_meets_threshold": compliance_data.get("compliance_rate", 0)
                >= 95,
                "overall_compliance": (
                    "valid"
                    if (
                        hash_result.get("response", "").strip()
                        == f'"{self.constitutional_hash}"'
                        and compliance_data.get("compliance_rate", 0) >= 95
                    )
                    else "invalid"
                ),
            }

        except Exception as e:
            logger.error(f"Error validating constitutional compliance: {e}")
            return {"status": "error", "error": str(e), "overall_compliance": "invalid"}

    async def validate_performance(self, environment: str) -> dict[str, Any]:
        """Validate performance metrics in target environment"""
        logger.info(f"📊 Validating performance in {environment} environment...")

        performance_results = {}
        namespace = self.namespaces[environment]

        # Performance thresholds
        thresholds = {
            "response_time_ms": 500,
            "cpu_usage_percent": 80,
            "memory_usage_percent": 80,
        }

        for service in self.services:
            service_name = f"acgs-{service['name']}-{environment}"

            try:
                # Measure response time
                start_time = time.time()
                health_check = await self.check_service_endpoint(
                    service_name, namespace, service["port"], service["health_path"]
                )
                response_time = (time.time() - start_time) * 1000  # Convert to ms

                # Get resource usage (simplified - would use metrics in production)
                resource_result = await self.run_kubectl_command(
                    [
                        "top",
                        "pods",
                        "-n",
                        namespace,
                        "-l",
                        f"app=acgs-{service['name']},environment={environment}",
                        "--no-headers",
                    ]
                )

                performance_results[service["name"]] = {
                    "response_time_ms": response_time,
                    "response_time_ok": response_time < thresholds["response_time_ms"],
                    "endpoint_healthy": health_check["status"] == "healthy",
                    "resource_usage": (
                        resource_result["stdout"]
                        if resource_result["returncode"] == 0
                        else "unavailable"
                    ),
                }

            except Exception as e:
                performance_results[service["name"]] = {
                    "status": "error",
                    "error": str(e),
                }

        # Overall performance assessment
        all_performing = all(
            result.get("response_time_ok", False)
            and result.get("endpoint_healthy", False)
            for result in performance_results.values()
            if isinstance(result, dict) and "response_time_ok" in result
        )

        performance_results["overall_performance"] = (
            "acceptable" if all_performing else "degraded"
        )

        return performance_results

    def should_switch_traffic(self, results: dict[str, Any]) -> bool:
        """Determine if traffic should be switched based on validation results"""

        # Check health
        health_ok = (
            results.get("health_check", {}).get("overall_environment_health")
            == "healthy"
        )

        # Check constitutional compliance
        compliance_ok = (
            results.get("compliance_check", {}).get("overall_compliance") == "valid"
        )

        # Check performance
        performance_ok = (
            results.get("performance_check", {}).get("overall_performance")
            == "acceptable"
        )

        logger.info(
            f"Traffic switch decision: health={health_ok}, compliance={compliance_ok}, performance={performance_ok}"
        )

        return health_ok and compliance_ok and performance_ok

    async def switch_traffic(self, from_env: str, to_env: str) -> dict[str, Any]:
        """Switch traffic from one environment to another"""
        logger.info(f"🔄 Switching traffic from {from_env} to {to_env}...")

        try:
            # Update traffic configuration
            result = await self.run_kubectl_command(
                [
                    "patch",
                    "configmap",
                    "acgs-traffic-config",
                    "-n",
                    self.namespaces["shared"],
                    "--type",
                    "merge",
                    "-p",
                    f'{{"data":{{"active-environment":"{to_env}"}}}}',
                ]
            )

            if result["returncode"] != 0:
                return {"status": "failed", "error": result["stderr"]}

            # Update service routing
            for service in self.services:
                service_result = await self.run_kubectl_command(
                    [
                        "patch",
                        "service",
                        f"acgs-{service['name']}-active",
                        "-n",
                        self.namespaces["shared"],
                        "--type",
                        "merge",
                        "-p",
                        f'{{"spec":{{"externalName":"acgs-{service["name"]}-{to_env}.{self.namespaces[to_env]}.svc.cluster.local"}}}}',
                    ]
                )

                if service_result["returncode"] != 0:
                    logger.error(
                        f"Failed to update {service['name']} routing: {service_result['stderr']}"
                    )

            # Wait for traffic switch to take effect
            await asyncio.sleep(10)

            # Verify traffic switch
            verification = await self.verify_traffic_switch(to_env)

            return {
                "status": "success",
                "from_environment": from_env,
                "to_environment": to_env,
                "verification": verification,
            }

        except Exception as e:
            logger.error(f"Error switching traffic: {e}")
            return {"status": "error", "error": str(e)}

    async def run_kubectl_command(self, args: list[str]) -> dict[str, Any]:
        """Run kubectl command and return result"""
        cmd = ["kubectl"] + args

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            return {
                "returncode": process.returncode,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "command": " ".join(cmd),
            }

        except Exception as e:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": str(e),
                "command": " ".join(cmd),
            }

    async def check_service_endpoint(
        self, service_name: str, namespace: str, port: int, path: str
    ) -> dict[str, Any]:
        """Check service endpoint health"""
        try:
            # Use kubectl port-forward to check endpoint
            cmd = [
                "kubectl",
                "exec",
                "-n",
                namespace,
                "deployment/" + service_name,
                "--",
                "curl",
                "-f",
                f"http://localhost:{port}{path}",
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)

            return {
                "status": "healthy" if process.returncode == 0 else "unhealthy",
                "response": stdout.decode(),
                "error": stderr.decode() if process.returncode != 0 else None,
            }

        except asyncio.TimeoutError:
            return {"status": "timeout", "error": "Health check timed out"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_environment_status(self, environment: str) -> dict[str, Any]:
        """Get detailed status of an environment"""
        namespace = self.namespaces[environment]

        try:
            # Get deployment status
            result = await self.run_kubectl_command(
                ["get", "deployments", "-n", namespace, "-o", "json"]
            )

            if result["returncode"] == 0:
                deployments = json.loads(result["stdout"])
                return {
                    "status": "running",
                    "deployments": len(deployments.get("items", [])),
                    "namespace": namespace,
                }
            return {"status": "error", "error": result["stderr"]}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def get_traffic_split(self) -> dict[str, Any]:
        """Get current traffic split configuration"""
        try:
            result = await self.run_kubectl_command(
                [
                    "get",
                    "configmap",
                    "acgs-traffic-config",
                    "-n",
                    self.namespaces["shared"],
                    "-o",
                    "jsonpath={.data.traffic-split}",
                ]
            )

            traffic_split = result["stdout"].strip() or "100:0"
            blue_percent, green_percent = map(int, traffic_split.split(":"))

            return {
                "blue_percent": blue_percent,
                "green_percent": green_percent,
                "split_string": traffic_split,
            }

        except Exception as e:
            return {"error": str(e)}

    async def verify_traffic_switch(self, target_env: str) -> dict[str, Any]:
        """Verify that traffic has been switched to target environment"""
        try:
            # Check active environment configuration
            result = await self.run_kubectl_command(
                [
                    "get",
                    "configmap",
                    "acgs-traffic-config",
                    "-n",
                    self.namespaces["shared"],
                    "-o",
                    "jsonpath={.data.active-environment}",
                ]
            )

            active_env = result["stdout"].strip()

            return {
                "config_updated": active_env == target_env,
                "active_environment": active_env,
                "target_environment": target_env,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def post_deployment_validation(self, environment: str) -> dict[str, Any]:
        """Perform post-deployment validation"""
        logger.info(f"✅ Performing post-deployment validation for {environment}...")

        validation = {}

        # Re-run health checks
        validation["final_health_check"] = await self.comprehensive_health_check(
            environment
        )

        # Re-validate constitutional compliance
        validation["final_compliance_check"] = (
            await self.validate_constitutional_compliance(environment)
        )

        # Check traffic routing
        validation["traffic_routing"] = await self.verify_traffic_switch(environment)

        return validation

    async def cleanup_old_environment(self, old_environment: str) -> dict[str, Any]:
        """Clean up old environment after successful deployment"""
        logger.info(f"🧹 Cleaning up {old_environment} environment...")

        # For now, just scale down to save resources
        # In production, you might want to keep it for quick rollback
        cleanup_results = {}
        namespace = self.namespaces[old_environment]

        try:
            for service in self.services:
                deployment_name = f"acgs-{service['name']}-{old_environment}"

                # Scale down to 1 replica (keep minimal for rollback)
                result = await self.run_kubectl_command(
                    [
                        "scale",
                        "deployment",
                        deployment_name,
                        "-n",
                        namespace,
                        "--replicas=1",
                    ]
                )

                cleanup_results[f"{service['name']}_scale_down"] = {
                    "status": "success" if result["returncode"] == 0 else "failed",
                    "deployment": deployment_name,
                }

            return cleanup_results

        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def emergency_rollback(self, rollback_environment: str) -> dict[str, Any]:
        """Emergency rollback to previous environment"""
        logger.warning(f"🚨 Performing emergency rollback to {rollback_environment}...")

        try:
            # Switch traffic back
            rollback_result = await self.switch_traffic("current", rollback_environment)

            # Scale up rollback environment if needed
            namespace = self.namespaces[rollback_environment]

            for service in self.services:
                deployment_name = f"acgs-{service['name']}-{rollback_environment}"

                await self.run_kubectl_command(
                    [
                        "scale",
                        "deployment",
                        deployment_name,
                        "-n",
                        namespace,
                        "--replicas=2",
                    ]
                )

            return {
                "status": "success",
                "rollback_environment": rollback_environment,
                "traffic_switch": rollback_result,
            }

        except Exception as e:
            logger.error(f"Emergency rollback failed: {e}")
            return {"status": "failed", "error": str(e)}

    def generate_deployment_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate deployment summary"""
        summary = {
            "validations_passed": 0,
            "validations_failed": 0,
            "services_healthy": 0,
            "services_total": len(self.services),
            "constitutional_compliance": "unknown",
            "performance_status": "unknown",
            "traffic_switched": False,
        }

        # Analyze results
        for component, result in results.items():
            if isinstance(result, dict):
                if result.get("overall_environment_health") == "healthy":
                    summary["validations_passed"] += 1
                elif result.get("overall_environment_health") == "unhealthy":
                    summary["validations_failed"] += 1

                if result.get("overall_compliance") == "valid":
                    summary["constitutional_compliance"] = "valid"
                elif result.get("overall_compliance") == "invalid":
                    summary["constitutional_compliance"] = "invalid"

                if result.get("overall_performance") == "acceptable":
                    summary["performance_status"] = "acceptable"
                elif result.get("overall_performance") == "degraded":
                    summary["performance_status"] = "degraded"

                if result.get("status") == "success" and "traffic" in component:
                    summary["traffic_switched"] = True

        return summary


async def main():
    """Main deployment function"""
    import argparse

    parser = argparse.ArgumentParser(description="ACGS-1 Blue-Green Deployment")
    parser.add_argument(
        "action",
        choices=["deploy", "switch", "status", "rollback"],
        help="Deployment action to perform",
    )
    parser.add_argument(
        "--environment",
        choices=["blue", "green"],
        default="green",
        help="Target environment for deployment",
    )
    parser.add_argument(
        "--image-tag", default="latest", help="Docker image tag to deploy"
    )
    parser.add_argument(
        "--force", action="store_true", help="Force deployment without validation"
    )

    args = parser.parse_args()

    deployer = BlueGreenDeployer()

    try:
        if args.action == "deploy":
            result = await deployer.deploy_blue_green_system(
                args.environment, args.image_tag
            )
        elif args.action == "status":
            result = await deployer.get_current_deployment_state()
        else:
            result = {"status": "not_implemented", "action": args.action}

        print("\n" + "=" * 80)
        print("BLUE-GREEN DEPLOYMENT RESULT")
        print("=" * 80)
        print(json.dumps(result, indent=2))

        if result.get("status") == "success":
            print("\n✅ Blue-Green deployment completed successfully!")
        else:
            print("\n❌ Blue-Green deployment failed.")

    except Exception as e:
        logger.error(f"Deployment error: {e}")
        print(f"\n❌ Deployment failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
