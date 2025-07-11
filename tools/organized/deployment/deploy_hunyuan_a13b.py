#!/usr/bin/env python3
"""
Deployment script for Hunyuan-A13B-Instruct model in ACGS
Handles Docker container deployment, health checks, and configuration.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import requests
import yaml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class HunyuanDeploymentManager:
    """Manages deployment of Hunyuan-A13B-Instruct model."""

    def __init__(self, config_path: str | None = None):
        self.config_path = config_path or "config/models/hunyuan-a13b.yaml"
        self.docker_compose_file = "docker-compose.hunyuan.yml"
        self.service_name = "hunyuan-a13b"
        self.base_url = "http://localhost:8000"

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load model configuration from YAML file."""
        try:
            with open(self.config_path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing configuration: {e}")
            sys.exit(1)

    def check_requirements(self) -> bool:
        """Check system requirements for Hunyuan deployment."""
        print("🔍 Checking system requirements...")

        # Check CUDA version
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=driver_version,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"✅ NVIDIA GPU detected: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ NVIDIA GPU or drivers not found. CUDA 12.8+ required.")
            return False

        # Check Docker
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            print("✅ Docker is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker not found. Please install Docker.")
            return False

        # Check Docker Compose
        try:
            subprocess.run(
                ["docker", "compose", "--version"], capture_output=True, check=True
            )
            print("✅ Docker Compose is available")
        except subprocess.CalledProcessError:
            print("❌ Docker Compose not found. Please install Docker Compose v2.")
            return False

        # Check available disk space (need ~100GB)
        import shutil

        free_space = shutil.disk_usage(".").free / (1024**3)  # GB
        if free_space < 100:
            print(
                f"⚠️  Warning: Only {free_space:.1f}GB free space. 100GB+ recommended."
            )
        else:
            print(f"✅ Sufficient disk space: {free_space:.1f}GB")

        return True

    def pull_docker_image(self, use_alternative: bool = False) -> bool:
        """Pull the Hunyuan Docker image."""
        print("📦 Pulling Hunyuan Docker image...")

        image = self.config["model_config"]["docker"]["image"]
        if use_alternative:
            image = self.config["model_config"]["docker"]["alternative_image"]

        try:
            subprocess.run(["docker", "pull", image], check=True)
            print(f"✅ Successfully pulled: {image}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to pull image: {e}")
            if not use_alternative:
                print("🔄 Trying alternative image...")
                return self.pull_docker_image(use_alternative=True)
            return False

    def prepare_directories(self):
        """Create necessary directories for deployment."""
        print("📁 Preparing directories...")

        directories = [
            "logs/hunyuan",
            "config/models",
            "config/monitoring",
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")

    def generate_monitoring_config(self):
        """Generate Prometheus monitoring configuration for Hunyuan."""
        print("📊 Generating monitoring configuration...")

        prometheus_config = {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "scrape_configs": [
                {
                    "job_name": "hunyuan-a13b",
                    "static_configs": [{"targets": ["localhost:8000"]}],
                    "metrics_path": "/metrics",
                    "scrape_interval": "10s",
                }
            ],
        }

        config_path = Path("config/monitoring/prometheus-hunyuan.yml")
        with open(config_path, "w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        print(f"✅ Created monitoring config: {config_path}")

    def start_service(self, download_source: str = "huggingface") -> bool:
        """Start the Hunyuan service using Docker Compose."""
        print(f"🚀 Starting Hunyuan service (source: {download_source})...")

        cmd = ["docker", "compose", "-f", self.docker_compose_file, "up", "-d"]

        if download_source == "modelscope":
            cmd.extend(["--profile", "modelscope", "hunyuan-a13b-modelscope"])
        else:
            cmd.append(self.service_name)

        try:
            subprocess.run(cmd, check=True)
            print("✅ Service started successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start service: {e}")
            return False

    def wait_for_model_ready(self, timeout: int = 300) -> bool:
        """Wait for the model to be ready and accepting requests."""
        print("⏳ Waiting for model to be ready...")

        start_time = time.time()
        health_url = f"{self.base_url}/health"

        while time.time() - start_time < timeout:
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    print("✅ Model is ready and healthy")
                    return True
            except requests.RequestException:
                pass

            # Show progress
            elapsed = int(time.time() - start_time)
            print(f"⏳ Waiting... ({elapsed}s/{timeout}s)", end="\r")
            time.sleep(10)

        print(f"\n❌ Model failed to become ready within {timeout} seconds")
        return False

    def test_model_inference(self) -> bool:
        """Test model inference with a simple request."""
        print("🧪 Testing model inference...")

        test_payload = {
            "model": "tencent/Hunyuan-A13B-Instruct",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello! Please respond in both English and Chinese to test multilingual capabilities.",
                }
            ],
            "max_tokens": 100,
            "temperature": 0.7,
        }

        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions", json=test_payload, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print("✅ Model inference successful")
                print(f"📝 Response preview: {content[:100]}...")
                return True
            print(f"❌ Inference failed: {response.status_code} - {response.text}")
            return False

        except requests.RequestException as e:
            print(f"❌ Inference test failed: {e}")
            return False

    def show_service_status(self):
        """Show current service status and logs."""
        print("📊 Service Status:")

        try:
            # Show container status
            result = subprocess.run(
                ["docker", "compose", "-f", self.docker_compose_file, "ps"],
                capture_output=True,
                text=True,
                check=True,
            )
            print(result.stdout)

            # Show recent logs
            print("\n📜 Recent logs:")
            subprocess.run(
                [
                    "docker",
                    "compose",
                    "-f",
                    self.docker_compose_file,
                    "logs",
                    "--tail=10",
                    self.service_name,
                ],
                check=True,
            )

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get service status: {e}")

    def stop_service(self):
        """Stop the Hunyuan service."""
        print("🛑 Stopping Hunyuan service...")

        try:
            subprocess.run(
                ["docker", "compose", "-f", self.docker_compose_file, "down"],
                check=True,
            )
            print("✅ Service stopped successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to stop service: {e}")

    def deploy(
        self, download_source: str = "huggingface", skip_tests: bool = False
    ) -> bool:
        """Complete deployment process."""
        print("🚀 Starting Hunyuan-A13B deployment for ACGS...")
        print("=" * 60)

        # Step 1: Check requirements
        if not self.check_requirements():
            return False

        # Step 2: Prepare environment
        self.prepare_directories()
        self.generate_monitoring_config()

        # Step 3: Pull Docker image
        if not self.pull_docker_image():
            return False

        # Step 4: Start service
        if not self.start_service(download_source):
            return False

        # Step 5: Wait for model to be ready
        if not self.wait_for_model_ready():
            print("📜 Checking logs for issues...")
            self.show_service_status()
            return False

        # Step 6: Test inference (optional)
        if not skip_tests:
            if not self.test_model_inference():
                print("⚠️  Model started but inference test failed")

        print("\n🎉 Hunyuan-A13B deployment completed successfully!")
        print(f"📡 API endpoint: {self.base_url}/v1")
        print(f"📊 Health check: {self.base_url}/health")
        print("📈 Monitoring: http://localhost:9090 (if enabled)")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Hunyuan-A13B-Instruct for ACGS"
    )
    parser.add_argument(
        "action", choices=["deploy", "stop", "status", "test"], help="Action to perform"
    )
    parser.add_argument(
        "--source",
        choices=["huggingface", "modelscope"],
        default="huggingface",
        help="Model download source",
    )
    parser.add_argument("--config", help="Path to model configuration file")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip inference tests during deployment",
    )

    args = parser.parse_args()

    # Create deployment manager
    manager = HunyuanDeploymentManager(args.config)

    if args.action == "deploy":
        success = manager.deploy(args.source, args.skip_tests)
        sys.exit(0 if success else 1)
    elif args.action == "stop":
        manager.stop_service()
    elif args.action == "status":
        manager.show_service_status()
    elif args.action == "test":
        if manager.test_model_inference():
            print("✅ Model test passed")
        else:
            print("❌ Model test failed")
            sys.exit(1)


if __name__ == "__main__":
    main()
