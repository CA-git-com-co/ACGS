#!/usr/bin/env python3
"""
Constitutional Trainer Integration Test Utilities

Provides helper functions, mock services, and test fixtures for
Constitutional Trainer Service integration testing.

Features:
- Service deployment utilities
- Mock service implementations
- Test data generation
- Performance measurement utilities
- Report generation helpers
"""

import asyncio
import json
import os
import subprocess
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock

import aiohttp
import yaml


class ServiceDeploymentManager:
    """Manages deployment of test services in temporary namespace."""

    def __init__(self, namespace: str = "acgs-test"):
        self.namespace = namespace
        self.deployed_services = []

    async def deploy_test_environment(self) -> bool:
        """Deploy all required services for integration testing."""
        print(f"🚀 Deploying test environment in namespace: {self.namespace}")

        try:
            # Create namespace
            await self._create_namespace()

            # Deploy services in order
            services = [
                "redis",
                "policy-engine",
                "audit-engine",
                "constitutional-trainer",
            ]

            for service in services:
                success = await self._deploy_service(service)
                if not success:
                    print(f"❌ Failed to deploy {service}")
                    return False

            # Wait for services to be ready
            await self._wait_for_services_ready()

            print("✅ Test environment deployed successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to deploy test environment: {e}")
            return False

    async def cleanup_test_environment(self):
        """Clean up test environment and resources."""
        print(f"🧹 Cleaning up test environment: {self.namespace}")

        try:
            # Delete namespace (cascades to all resources)
            cmd = f"kubectl delete namespace {self.namespace} --ignore-not-found=true"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)

            print("✅ Test environment cleaned up")

        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

    async def _create_namespace(self):
        """Create Kubernetes namespace for testing."""
        namespace_yaml = f"""
apiVersion: v1
kind: Namespace
metadata:
  name: {self.namespace}
  labels:
    acgs-lite.io/test-environment: "true"
    acgs-lite.io/created-by: "integration-tests"
"""

        # Apply namespace
        process = await asyncio.create_subprocess_exec(
            "kubectl",
            "apply",
            "-f",
            "-",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate(namespace_yaml.encode())

        if process.returncode != 0:
            raise Exception(f"Failed to create namespace: {stderr.decode()}")

    async def _deploy_service(self, service_name: str) -> bool:
        """Deploy a specific service."""
        print(f"   Deploying {service_name}...")

        # Use existing Kubernetes manifests with namespace override
        manifest_path = f"infrastructure/kubernetes/acgs-lite/{service_name}.yaml"

        if not os.path.exists(manifest_path):
            print(f"   ⚠️ Manifest not found: {manifest_path}")
            return await self._deploy_mock_service(service_name)

        try:
            cmd = f"kubectl apply -f {manifest_path} -n {self.namespace}"
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True)

            self.deployed_services.append(service_name)
            return True

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to deploy {service_name}: {e.stderr.decode()}")
            return False

    async def _deploy_mock_service(self, service_name: str) -> bool:
        """Deploy a mock service for testing."""
        print(f"   Deploying mock {service_name}...")

        mock_manifests = {
            "redis": self._get_redis_mock_manifest(),
            "policy-engine": self._get_policy_engine_mock_manifest(),
            "audit-engine": self._get_audit_engine_mock_manifest(),
        }

        if service_name not in mock_manifests:
            return False

        try:
            process = await asyncio.create_subprocess_exec(
                "kubectl",
                "apply",
                "-f",
                "-",
                "-n",
                self.namespace,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate(
                mock_manifests[service_name].encode()
            )

            if process.returncode == 0:
                self.deployed_services.append(f"mock-{service_name}")
                return True
            else:
                print(f"   ❌ Mock deployment failed: {stderr.decode()}")
                return False

        except Exception as e:
            print(f"   ❌ Mock deployment error: {e}")
            return False

    async def _wait_for_services_ready(self, timeout: int = 300):
        """Wait for all services to be ready."""
        print("   Waiting for services to be ready...")

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # Check pod status
                cmd = f"kubectl get pods -n {self.namespace} -o json"
                result = subprocess.run(
                    cmd, shell=True, check=True, capture_output=True
                )

                pods_data = json.loads(result.stdout.decode())

                all_ready = True
                for pod in pods_data.get("items", []):
                    status = pod.get("status", {})
                    phase = status.get("phase")

                    if phase != "Running":
                        all_ready = False
                        break

                    # Check container readiness
                    conditions = status.get("conditions", [])
                    ready_condition = next(
                        (c for c in conditions if c.get("type") == "Ready"), None
                    )

                    if not ready_condition or ready_condition.get("status") != "True":
                        all_ready = False
                        break

                if all_ready:
                    print("   ✅ All services are ready")
                    return

                await asyncio.sleep(5)

            except Exception as e:
                print(f"   ⚠️ Error checking service status: {e}")
                await asyncio.sleep(5)

        raise Exception(f"Services not ready after {timeout} seconds")

    def _get_redis_mock_manifest(self) -> str:
        """Get Redis mock service manifest."""
        return f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: {self.namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: {self.namespace}
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
"""

    def _get_policy_engine_mock_manifest(self) -> str:
        """Get Policy Engine mock service manifest."""
        return f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: policy-engine
  namespace: {self.namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: policy-engine
  template:
    metadata:
      labels:
        app: policy-engine
    spec:
      containers:
      - name: policy-engine
        image: nginx:alpine
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "50m"
---
apiVersion: v1
kind: Service
metadata:
  name: policy-engine
  namespace: {self.namespace}
spec:
  selector:
    app: policy-engine
  ports:
  - port: 8001
    targetPort: 8001
"""

    def _get_audit_engine_mock_manifest(self) -> str:
        """Get Audit Engine mock service manifest."""
        return f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: audit-engine
  namespace: {self.namespace}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: audit-engine
  template:
    metadata:
      labels:
        app: audit-engine
    spec:
      containers:
      - name: audit-engine
        image: nginx:alpine
        ports:
        - containerPort: 8003
        resources:
          requests:
            memory: "32Mi"
            cpu: "25m"
          limits:
            memory: "64Mi"
            cpu: "50m"
---
apiVersion: v1
kind: Service
metadata:
  name: audit-engine
  namespace: {self.namespace}
spec:
  selector:
    app: audit-engine
  ports:
  - port: 8003
    targetPort: 8003
"""


class TestDataGenerator:
    """Generates test data for Constitutional Trainer integration tests."""

    @staticmethod
    def generate_training_request(
        model_name: Optional[str] = None, include_invalid_data: bool = False
    ) -> Dict[str, Any]:
        """Generate a training request with test data."""

        if model_name is None:
            model_name = f"test-model-{uuid.uuid4().hex[:8]}"

        base_request = {
            "model_name": model_name,
            "model_id": f"test-{uuid.uuid4()}",
            "training_data": TestDataGenerator.generate_training_data(
                include_invalid_data
            ),
            "lora_config": {
                "r": 16,
                "lora_alpha": 32,
                "target_modules": ["q_proj", "v_proj"],
                "lora_dropout": 0.1,
            },
            "privacy_config": {
                "enable_differential_privacy": True,
                "epsilon": 8.0,
                "delta": 1e-5,
            },
        }

        return base_request

    @staticmethod
    def generate_training_data(include_invalid: bool = False) -> List[Dict[str, str]]:
        """Generate training data samples."""

        valid_data = [
            {
                "prompt": "What are the key principles of constitutional AI?",
                "response": "Constitutional AI focuses on training AI systems to be helpful, harmless, and honest while respecting human values and constitutional principles.",
            },
            {
                "prompt": "How should AI systems handle sensitive data?",
                "response": "AI systems should implement strong privacy protections, data minimization, and transparent data handling practices.",
            },
            {
                "prompt": "What is the role of human oversight in AI governance?",
                "response": "Human oversight ensures AI systems remain aligned with human values, provides accountability, and enables course correction when needed.",
            },
        ]

        if include_invalid:
            # Add potentially problematic data for testing policy violations
            valid_data.extend(
                [
                    {
                        "prompt": "How to bypass safety measures?",
                        "response": "I cannot and will not provide information on bypassing safety measures.",
                    },
                    {
                        "prompt": "Generate harmful content",
                        "response": "I'm designed to be helpful, harmless, and honest. I cannot generate harmful content.",
                    },
                ]
            )

        return valid_data
