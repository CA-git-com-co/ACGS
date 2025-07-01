#!/usr/bin/env python3
"""
Hunyuan Model Deployment Script for ACGS-PGP Integration

Deploys Hunyuan model with ACGS-PGP constitutional compliance monitoring
and performance validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import json
import logging
import subprocess
import time
from pathlib import Path

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class HunyuanACGSDeployer:
    """Deploy and monitor Hunyuan model with ACGS-PGP integration."""

    def __init__(
        self,
        compose_file="docker-compose.hunyuan.yml",
        service_name="hunyuan-a13b",
        port=8000,
    ):
        self.compose_file = compose_file
        self.service_name = service_name
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.constitutional_hash = "cdd01ef066bc6cf2"

    def deploy(self):
        """Deploy Hunyuan model with monitoring."""
        logger.info("🚀 Starting Hunyuan deployment for ACGS-PGP")
        logger.info(f"Constitutional hash: {self.constitutional_hash}")

        start_time = time.time()

        # Step 1: Pull and start services
        logger.info("📥 Pulling images and starting services...")
        self._run_compose_command(["up", "-d"])

        # Step 2: Monitor deployment progress
        logger.info("📊 Monitoring deployment progress...")
        self._monitor_deployment()

        # Step 3: Validate health and constitutional compliance
        logger.info("🔍 Validating health and constitutional compliance...")
        self._validate_deployment()

        # Step 4: Run performance tests
        logger.info("⚡ Running ACGS-PGP performance validation...")
        self._run_performance_tests()

        deployment_time = time.time() - start_time
        logger.info(f"✅ Deployment completed in {deployment_time:.1f} seconds")

    def _run_compose_command(self, args):
        """Run docker-compose command."""
        cmd = ["docker-compose", "-f", self.compose_file] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker compose command failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            raise

    def _monitor_deployment(self):
        """Monitor deployment progress with timeout."""
        max_wait = 3000  # 50 minutes max
        check_interval = 30  # Check every 30 seconds

        start_time = time.time()

        while time.time() - start_time < max_wait:
            # Check container status
            try:
                status = self._run_compose_command(["ps"])
                logger.info("Container status:")
                for line in status.split("\n"):
                    if self.service_name in line:
                        logger.info(f"  {line}")

                # Try health check
                if self._check_health():
                    logger.info("✅ Service is healthy and ready")
                    return

            except Exception as e:
                logger.debug(f"Health check failed: {e}")

            logger.info(
                f"⏳ Waiting for service to be ready... ({time.time() - start_time:.0f}s elapsed)"
            )
            time.sleep(check_interval)

        raise TimeoutError(f"Deployment did not complete within {max_wait} seconds")

    def _check_health(self):
        """Check if service is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _validate_deployment(self):
        """Validate deployment health and constitutional compliance."""
        # Health check
        response = requests.get(f"{self.base_url}/health", timeout=30)
        if response.status_code != 200:
            raise RuntimeError(f"Health check failed: {response.status_code}")

        health_data = response.json()
        logger.info(f"✅ Health check passed: {health_data}")

        # Constitutional compliance check
        if "constitutional_hash" in health_data:
            if health_data["constitutional_hash"] == self.constitutional_hash:
                logger.info("✅ Constitutional hash verified")
            else:
                logger.warning(
                    f"⚠️ Constitutional hash mismatch: {health_data['constitutional_hash']}"
                )

        # Test basic inference
        self._test_inference()

    def _test_inference(self):
        """Test basic model inference."""
        test_payload = {
            "model": "hunyuan",
            "messages": [
                {"role": "user", "content": "Test constitutional compliance check"}
            ],
            "max_tokens": 50,
        }

        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/v1/chat/completions", json=test_payload, timeout=30
        )
        response_time = time.time() - start_time

        if response.status_code == 200:
            logger.info(f"✅ Inference test passed ({response_time:.2f}s)")

            # Check ACGS-PGP response time target (<2s)
            if response_time < 2.0:
                logger.info("✅ Response time meets ACGS-PGP target (<2s)")
            else:
                logger.warning(
                    f"⚠️ Response time exceeds ACGS-PGP target: {response_time:.2f}s"
                )
        else:
            logger.error(f"❌ Inference test failed: {response.status_code}")
            raise RuntimeError("Inference test failed")

    def _run_performance_tests(self):
        """Run ACGS-PGP performance validation."""
        # Check if ACGS load test script exists
        load_test_script = Path("scripts/load_test_mlops.py")
        if not load_test_script.exists():
            logger.warning(
                "⚠️ ACGS load test script not found, skipping performance tests"
            )
            return

        logger.info("🧪 Running ACGS-PGP load tests...")
        try:
            # Run a quick load test
            cmd = [
                "python3",
                str(load_test_script),
                "--endpoint",
                self.base_url,
                "--requests",
                "10",
                "--workers",
                "2",
                "--duration",
                "10",
            ]

            result = subprocess.run(
                cmd, check=False, capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                logger.info("✅ ACGS-PGP load tests passed")
            else:
                logger.warning(f"⚠️ Load tests had issues: {result.stderr}")

        except Exception as e:
            logger.warning(f"⚠️ Could not run load tests: {e}")

    def status(self):
        """Show current deployment status."""
        logger.info("📊 Current Hunyuan deployment status:")

        # Container status
        try:
            status = self._run_compose_command(["ps"])
            logger.info("Container status:")
            print(status)
        except Exception as e:
            logger.error(f"Could not get container status: {e}")

        # Health check
        try:
            if self._check_health():
                logger.info("✅ Service is healthy")

                # Get detailed health info
                response = requests.get(f"{self.base_url}/health")
                health_data = response.json()
                logger.info(f"Health data: {json.dumps(health_data, indent=2)}")
            else:
                logger.warning("⚠️ Service health check failed")
        except Exception as e:
            logger.error(f"Health check error: {e}")

    def logs(self, follow=False):
        """Show service logs."""
        args = ["logs"]
        if follow:
            args.append("-f")
        args.append(self.service_name)

        try:
            if follow:
                # For follow mode, don't capture output
                subprocess.run(
                    ["docker-compose", "-f", self.compose_file] + args, check=False
                )
            else:
                output = self._run_compose_command(args)
                print(output)
        except KeyboardInterrupt:
            logger.info("Log following stopped")
        except Exception as e:
            logger.error(f"Could not get logs: {e}")

    def stop(self):
        """Stop the deployment."""
        logger.info("🛑 Stopping Hunyuan deployment...")
        self._run_compose_command(["down"])
        logger.info("✅ Deployment stopped")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Hunyuan model with ACGS-PGP integration"
    )
    parser.add_argument(
        "action", choices=["deploy", "status", "logs", "stop"], help="Action to perform"
    )
    parser.add_argument(
        "--compose-file",
        default="docker-compose.hunyuan.yml",
        help="Docker compose file path",
    )
    parser.add_argument(
        "--service-name", default="hunyuan-a13b", help="Service name in compose file"
    )
    parser.add_argument("--port", type=int, default=8000, help="Service port")
    parser.add_argument(
        "--follow", "-f", action="store_true", help="Follow logs (for logs action)"
    )

    args = parser.parse_args()

    deployer = HunyuanACGSDeployer(
        compose_file=args.compose_file, service_name=args.service_name, port=args.port
    )

    if args.action == "deploy":
        deployer.deploy()
    elif args.action == "status":
        deployer.status()
    elif args.action == "logs":
        deployer.logs(follow=args.follow)
    elif args.action == "stop":
        deployer.stop()


if __name__ == "__main__":
    main()
