#!/usr/bin/env python3
"""
Debug Service Startup Issues
Detailed analysis of why services are failing health checks
"""

import asyncio
import json
import os
import subprocess
import time
from pathlib import Path

import httpx

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ServiceStartupDebugger:
    """Debug service startup issues with detailed logging."""

    def __init__(self):
        self.project_root = Path("/home/dislove/ACGS-1")
        self.service_dirs = {
            "ac_service": self.project_root
            / "services"
            / "core"
            / "constitutional-ai"
            / "ac_service",
            "integrity_service": self.project_root
            / "services"
            / "platform"
            / "integrity"
            / "integrity_service",
            "fv_service": self.project_root
            / "services"
            / "core"
            / "formal-verification"
            / "fv_service",
            "gs_service": self.project_root
            / "services"
            / "core"
            / "governance-synthesis"
            / "gs_service",
        }

        self.service_ports = {
            "ac_service": 8001,
            "integrity_service": 8002,
            "fv_service": 8003,
            "gs_service": 8004,
        }

    def check_service_directory(self, service_name: str):
        """Check if service directory and main.py exist."""
        service_dir = self.service_dirs[service_name]
        print(f"\n🔍 Checking {service_name} directory structure:")
        print(f"   Directory: {service_dir}")
        print(f"   Exists: {service_dir.exists()}")

        if service_dir.exists():
            main_py = service_dir / "app" / "main.py"
            print(f"   main.py: {main_py.exists()} ({main_py})")

            # Check for requirements.txt
            req_files = [
                service_dir / "requirements.txt",
                service_dir / "app" / "requirements.txt",
                self.project_root / "services" / "shared" / "requirements.txt",
            ]

            for req_file in req_files:
                if req_file.exists():
                    print(f"   requirements.txt: ✅ {req_file}")
                    break
            else:
                print("   requirements.txt: ❌ Not found")

            # List directory contents
            if service_dir.exists():
                contents = list(service_dir.iterdir())
                print(f"   Contents: {[p.name for p in contents[:10]]}")

        return service_dir.exists()

    def check_python_dependencies(self, service_name: str):
        """Check if Python dependencies are available."""
        self.service_dirs[service_name]
        print(f"\n🐍 Checking Python dependencies for {service_name}:")

        # Try importing key modules
        test_imports = ["fastapi", "uvicorn", "httpx", "sqlalchemy", "pydantic"]

        for module in test_imports:
            try:
                result = subprocess.run(
                    ["python", "-c", f'import {module}; print(f"{module}: OK")'],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    print(f"   ✅ {module}: Available")
                else:
                    print(f"   ❌ {module}: {result.stderr.strip()}")
            except Exception as e:
                print(f"   ❌ {module}: {e}")

    async def test_service_startup_detailed(self, service_name: str):
        """Test service startup with detailed logging."""
        port = self.service_ports[service_name]
        service_dir = self.service_dirs[service_name]

        print(f"\n🚀 Testing detailed startup for {service_name}:")

        # Kill existing processes
        try:
            subprocess.run(
                ["pkill", "-f", f"uvicorn.*{port}"], capture_output=True, check=False
            )
            time.sleep(2)
        except:
            pass

        # Set environment variables
        env = os.environ.copy()
        env.update(
            {
                "AC_SERVICE_URL": "http://localhost:8001",
                "INTEGRITY_SERVICE_URL": "http://localhost:8002",
                "FV_SERVICE_URL": "http://localhost:8003",
                "GS_SERVICE_URL": "http://localhost:8004",
                "PGC_SERVICE_URL": "http://localhost:8005",
                "EC_SERVICE_URL": "http://localhost:8006",
                "AUTH_SERVICE_URL": "http://localhost:8000",
                "SERVICE_DISCOVERY_ENABLED": "true",
                "HEALTH_CHECK_TIMEOUT": "5.0",
                "REQUEST_TIMEOUT": "30.0",
                "LOG_LEVEL": "INFO",
                "PYTHONPATH": str(self.project_root / "services" / "shared"),
            }
        )

        # Start the service with detailed output
        cmd = [
            "python",
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
            "--log-level",
            "debug",
        ]

        print(f"   Command: {' '.join(cmd)}")
        print(f"   Working directory: {service_dir}")
        print(f"   Environment variables: {[k for k in env.keys() if 'SERVICE' in k]}")

        try:
            # Start process and capture output
            process = subprocess.Popen(
                cmd,
                cwd=service_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )

            print(f"   Process started with PID: {process.pid}")

            # Wait and capture initial output
            time.sleep(5)

            # Check if process is still running
            if process.poll() is None:
                print("   ✅ Process is still running")

                # Try to get some output
                try:
                    stdout, stderr = process.communicate(timeout=3)
                    print(f"   Output (first 500 chars): {stdout[:500]}")
                except subprocess.TimeoutExpired:
                    print("   Process still running, checking health...")

                    # Test health endpoint
                    health_result = await self.test_health_endpoint(port)
                    print(
                        f"   Health check: {'✅ PASS' if health_result else '❌ FAIL'}"
                    )

                    # Kill the process for cleanup
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except:
                        process.kill()

                    return health_result
            else:
                stdout, stderr = process.communicate()
                print(f"   ❌ Process exited with code: {process.returncode}")
                print(f"   Output: {stdout}")
                return False

        except Exception as e:
            print(f"   ❌ Failed to start: {e}")
            return False

    async def test_health_endpoint(self, port: int) -> bool:
        """Test health endpoint with detailed error reporting."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"http://localhost:{port}/health")
                print(f"      Health response: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"      Health data: {json.dumps(data, indent=2)[:200]}...")
                    return True
                print(f"      Health error: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"      Health exception: {e}")
            return False

    async def run_comprehensive_debug(self):
        """Run comprehensive debugging for all failed services."""
        print("🔧 ACGS-1 Service Startup Debugging")
        print("=" * 50)

        for service_name in self.service_dirs.keys():
            print(f"\n{'=' * 20} {service_name.upper()} {'=' * 20}")

            # Check directory structure
            dir_ok = self.check_service_directory(service_name)

            if dir_ok:
                # Check Python dependencies
                self.check_python_dependencies(service_name)

                # Test detailed startup
                startup_ok = await self.test_service_startup_detailed(service_name)

                print(f"\n📊 {service_name} Summary:")
                print(f"   Directory: {'✅' if dir_ok else '❌'}")
                print(f"   Startup: {'✅' if startup_ok else '❌'}")
            else:
                print(f"\n📊 {service_name} Summary:")
                print("   Directory: ❌ - Cannot proceed")


async def main():
    """Main debugging function."""
    debugger = ServiceStartupDebugger()
    await debugger.run_comprehensive_debug()


if __name__ == "__main__":
    asyncio.run(main())
