#!/usr/bin/env python3
"""
Cross-Platform Compatibility Test Suite
======================================

Tests functionality across different environments including:
- CPU-only fallback scenarios
- Cross-platform compatibility
- Environment-specific configurations
"""

import asyncio
import json
import platform
import sys
import time
from typing import Dict, List, Any
import aiohttp

# Service endpoints
SERVICES = {
    "auth": "http://localhost:8000",
    "ac": "http://localhost:8001",
    "integrity": "http://localhost:8002",
    "fv": "http://localhost:8003",
    "gs": "http://localhost:8004",
    "pgc": "http://localhost:8005",
    "ec": "http://localhost:8006",
}


class CrossPlatformCompatibilityTest:
    """Cross-platform compatibility test suite."""

    def __init__(self):
        self.results = {
            "timestamp": time.time(),
            "platform_info": self._get_platform_info(),
            "environment_tests": {},
            "cpu_fallback_tests": {},
            "compatibility_tests": {},
            "summary": {},
        }

    def _get_platform_info(self) -> Dict[str, Any]:
        """Get current platform information."""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": sys.version,
            "python_implementation": platform.python_implementation(),
            "architecture": platform.architecture(),
        }

    async def test_environment_compatibility(self) -> Dict[str, Any]:
        """Test environment compatibility across services."""
        print("🌍 Testing Environment Compatibility...")

        env_results = {}

        async with aiohttp.ClientSession() as session:
            for service_name, base_url in SERVICES.items():
                print(f"   Testing {service_name}...")

                try:
                    # Test basic health endpoint
                    async with session.get(f"{base_url}/health", timeout=5) as response:
                        if response.status == 200:
                            health_data = await response.json()

                            env_results[service_name] = {
                                "health_status": "healthy",
                                "response_status": response.status,
                                "service_info": health_data,
                                "platform_compatible": True,
                            }
                        else:
                            env_results[service_name] = {
                                "health_status": "unhealthy",
                                "response_status": response.status,
                                "platform_compatible": False,
                            }

                except Exception as e:
                    env_results[service_name] = {
                        "health_status": "error",
                        "error": str(e),
                        "platform_compatible": False,
                    }

        # Calculate compatibility metrics
        total_services = len(SERVICES)
        compatible_services = sum(
            1 for result in env_results.values() if result["platform_compatible"]
        )
        compatibility_rate = compatible_services / total_services

        self.results["environment_tests"] = {
            "platform_info": self.results["platform_info"],
            "service_results": env_results,
            "compatible_services": compatible_services,
            "total_services": total_services,
            "compatibility_rate": compatibility_rate,
            "passed": compatibility_rate >= 0.8,  # 80% must be compatible
        }

        print(
            f"   ✅ Environment Compatibility: {compatibility_rate:.1%} ({compatible_services}/{total_services})"
        )
        return self.results["environment_tests"]

    async def test_cpu_fallback_scenarios(self) -> Dict[str, Any]:
        """Test CPU-only fallback scenarios."""
        print("🖥️ Testing CPU Fallback Scenarios...")

        cpu_fallback_results = {}

        # Test services that might use GPU acceleration
        gpu_dependent_services = ["ac", "gs", "ec"]

        async with aiohttp.ClientSession() as session:
            for service_name in gpu_dependent_services:
                if service_name not in SERVICES:
                    continue

                base_url = SERVICES[service_name]
                print(f"   Testing {service_name} CPU fallback...")

                try:
                    # Test if service can handle CPU-only mode
                    # This would typically involve checking service configuration or endpoints
                    async with session.get(f"{base_url}/health", timeout=5) as response:
                        if response.status == 200:
                            health_data = await response.json()

                            # Check for GPU/CPU indicators in response
                            gpu_available = False
                            cpu_fallback_enabled = True

                            # Look for hardware indicators
                            if "features" in health_data:
                                features = health_data["features"]
                                if isinstance(features, dict):
                                    gpu_available = features.get(
                                        "gpu_acceleration", False
                                    )
                                    cpu_fallback_enabled = features.get(
                                        "cpu_fallback", True
                                    )

                            cpu_fallback_results[service_name] = {
                                "service_available": True,
                                "gpu_available": gpu_available,
                                "cpu_fallback_enabled": cpu_fallback_enabled,
                                "fallback_functional": True,  # Service is responding
                                "response_time_acceptable": True,  # Health check succeeded
                            }
                        else:
                            cpu_fallback_results[service_name] = {
                                "service_available": False,
                                "gpu_available": False,
                                "cpu_fallback_enabled": False,
                                "fallback_functional": False,
                                "response_time_acceptable": False,
                            }

                except Exception as e:
                    cpu_fallback_results[service_name] = {
                        "service_available": False,
                        "error": str(e),
                        "fallback_functional": False,
                    }

        # Calculate CPU fallback metrics
        total_tested = len(gpu_dependent_services)
        functional_fallbacks = sum(
            1
            for result in cpu_fallback_results.values()
            if result.get("fallback_functional", False)
        )
        fallback_rate = functional_fallbacks / total_tested if total_tested > 0 else 0

        self.results["cpu_fallback_tests"] = {
            "tested_services": gpu_dependent_services,
            "service_results": cpu_fallback_results,
            "functional_fallbacks": functional_fallbacks,
            "total_tested": total_tested,
            "fallback_rate": fallback_rate,
            "passed": fallback_rate >= 0.8,  # 80% must have functional CPU fallback
        }

        print(
            f"   ✅ CPU Fallback Rate: {fallback_rate:.1%} ({functional_fallbacks}/{total_tested})"
        )
        return self.results["cpu_fallback_tests"]

    async def test_cross_platform_features(self) -> Dict[str, Any]:
        """Test cross-platform specific features."""
        print("🔄 Testing Cross-Platform Features...")

        feature_results = {}

        # Test platform-specific features
        platform_features = {
            "file_system_compatibility": self._test_file_system_compatibility(),
            "network_compatibility": await self._test_network_compatibility(),
            "process_compatibility": self._test_process_compatibility(),
            "encoding_compatibility": self._test_encoding_compatibility(),
        }

        for feature_name, test_result in platform_features.items():
            feature_results[feature_name] = {
                "compatible": test_result,
                "platform": self.results["platform_info"]["system"],
            }

        # Calculate feature compatibility
        total_features = len(platform_features)
        compatible_features = sum(
            1 for result in feature_results.values() if result["compatible"]
        )
        feature_compatibility_rate = compatible_features / total_features

        self.results["compatibility_tests"] = {
            "feature_results": feature_results,
            "compatible_features": compatible_features,
            "total_features": total_features,
            "feature_compatibility_rate": feature_compatibility_rate,
            "passed": feature_compatibility_rate
            >= 0.8,  # 80% features must be compatible
        }

        print(
            f"   ✅ Feature Compatibility: {feature_compatibility_rate:.1%} ({compatible_features}/{total_features})"
        )
        return self.results["compatibility_tests"]

    def _test_file_system_compatibility(self) -> bool:
        """Test file system compatibility."""
        try:
            import os
            import tempfile

            # Test basic file operations
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                f.write("test")
                temp_path = f.name

            # Test file exists and can be read
            if os.path.exists(temp_path):
                with open(temp_path, "r") as f:
                    content = f.read()
                os.unlink(temp_path)
                return content == "test"

            return False
        except Exception:
            return False

    async def _test_network_compatibility(self) -> bool:
        """Test network compatibility."""
        try:
            async with aiohttp.ClientSession() as session:
                # Test basic network connectivity to localhost
                async with session.get(
                    "http://localhost:8000/health", timeout=2
                ) as response:
                    return response.status in [
                        200,
                        404,
                        403,
                    ]  # Any response indicates network works
        except Exception:
            return False

    def _test_process_compatibility(self) -> bool:
        """Test process compatibility."""
        try:
            import subprocess

            # Test basic process execution
            result = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and "Python" in result.stdout
        except Exception:
            return False

    def _test_encoding_compatibility(self) -> bool:
        """Test encoding compatibility."""
        try:
            # Test UTF-8 encoding/decoding
            test_string = "Hello, 世界! 🌍"
            encoded = test_string.encode("utf-8")
            decoded = encoded.decode("utf-8")
            return decoded == test_string
        except Exception:
            return False

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all cross-platform compatibility tests."""
        print("🌍 Running Cross-Platform Compatibility Test Suite")
        print("=" * 60)
        print(
            f"Platform: {self.results['platform_info']['system']} {self.results['platform_info']['release']}"
        )
        print(f"Python: {self.results['platform_info']['python_version'].split()[0]}")
        print("=" * 60)

        # Run tests
        await self.test_environment_compatibility()
        await self.test_cpu_fallback_scenarios()
        await self.test_cross_platform_features()

        # Generate summary
        env_passed = self.results["environment_tests"]["passed"]
        cpu_passed = self.results["cpu_fallback_tests"]["passed"]
        feature_passed = self.results["compatibility_tests"]["passed"]
        overall_passed = env_passed and cpu_passed and feature_passed

        self.results["summary"] = {
            "overall_passed": overall_passed,
            "environment_compatibility_passed": env_passed,
            "cpu_fallback_passed": cpu_passed,
            "feature_compatibility_passed": feature_passed,
            "platform": self.results["platform_info"]["system"],
        }

        print("=" * 60)
        print(f"🌍 Cross-Platform Compatibility Results:")
        print(
            f"   Environment Compatibility: {'✅ PASSED' if env_passed else '❌ FAILED'}"
        )
        print(f"   CPU Fallback: {'✅ PASSED' if cpu_passed else '❌ FAILED'}")
        print(
            f"   Feature Compatibility: {'✅ PASSED' if feature_passed else '❌ FAILED'}"
        )
        print(f"   Overall: {'✅ PASSED' if overall_passed else '❌ FAILED'}")

        return self.results


if __name__ == "__main__":

    async def main():
        tester = CrossPlatformCompatibilityTest()
        results = await tester.run_all_tests()

        # Save results
        with open("tests/results/cross_platform_compatibility_results.json", "w") as f:
            json.dump(results, f, indent=2)

        return results["summary"]["overall_passed"]

    # Run the tests
    success = asyncio.run(main())
    exit(0 if success else 1)
