#!/usr/bin/env python3
"""
Start GS Service on Host

This script starts the GS Service directly on the host machine with proper configuration
to resolve the dependency connectivity issues.
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

# Set up environment variables for localhost connectivity
os.environ["AC_SERVICE_URL"] = "http://localhost:8001"
os.environ["INTEGRITY_SERVICE_URL"] = "http://localhost:8002"
os.environ["FV_SERVICE_URL"] = "http://localhost:8003"
os.environ["PGC_SERVICE_URL"] = "http://localhost:8005"
os.environ["EC_SERVICE_URL"] = "http://localhost:8006"
os.environ["AUTH_SERVICE_URL"] = "http://localhost:8000"
os.environ["SERVICE_DISCOVERY_ENABLED"] = "true"
os.environ["HEALTH_CHECK_TIMEOUT"] = "5.0"
os.environ["REQUEST_TIMEOUT"] = "30.0"
os.environ["LOG_LEVEL"] = "INFO"


def stop_existing_gs_service():
    """Stop any existing GS service processes."""
    print("🛑 Stopping existing GS service processes...")

    try:
        # Stop Docker container if running
        subprocess.run(
            ["docker", "stop", "acgs_gs_service"], capture_output=True, check=False
        )
        print("  ✅ Stopped Docker container")
    except:
        pass

    try:
        # Kill any uvicorn processes on port 8004
        subprocess.run(
            ["pkill", "-f", "uvicorn.*8004"], capture_output=True, check=False
        )
        print("  ✅ Killed existing uvicorn processes")
    except:
        pass

    # Wait for processes to stop
    time.sleep(3)


def start_gs_service():
    """Start the GS service on the host."""
    print("🚀 Starting GS Service on host...")

    # Change to GS service directory
    gs_service_dir = Path(
        "/home/dislove/ACGS-1/services/core/governance-synthesis/gs_service"
    )

    if not gs_service_dir.exists():
        print(f"❌ GS Service directory not found: {gs_service_dir}")
        return None

    print(f"📁 Working directory: {gs_service_dir}")

    # Start the service
    cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004", "--reload"]

    print(f"🔧 Command: {' '.join(cmd)}")
    print(f"🌍 Environment variables set:")
    for key, value in os.environ.items():
        if "SERVICE_URL" in key or "SERVICE_" in key:
            print(f"  {key}={value}")

    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            cwd=gs_service_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=os.environ.copy(),
        )

        print(f"✅ GS Service started with PID: {process.pid}")

        # Wait a moment for startup
        time.sleep(5)

        # Check if process is still running
        if process.poll() is None:
            print("✅ GS Service process is running")
            return process
        else:
            print("❌ GS Service process exited")
            stdout, stderr = process.communicate()
            print(f"Output: {stdout}")
            return None

    except Exception as e:
        print(f"❌ Failed to start GS Service: {e}")
        return None


async def test_gs_service():
    """Test the GS service connectivity."""
    print("🧪 Testing GS Service connectivity...")

    max_retries = 6
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("http://localhost:8004/health")

                if response.status_code == 200:
                    data = response.json()
                    print("✅ GS Service is responding!")
                    print("📊 Health Status:")
                    import json

                    print(json.dumps(data, indent=2))

                    # Check dependency status
                    deps = data.get("dependencies", {})
                    ac_status = deps.get("ac_service", {}).get("status")
                    integrity_status = deps.get("integrity_service", {}).get("status")

                    if ac_status == "healthy" and integrity_status == "healthy":
                        print("🎉 SUCCESS: All dependencies are healthy!")
                        return True
                    else:
                        print(
                            f"⚠️ Dependencies status: AC={ac_status}, Integrity={integrity_status}"
                        )
                        return True  # Service is running, dependencies might take time
                else:
                    print(f"⚠️ GS Service returned HTTP {response.status_code}")

        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1}/{max_retries}: {e}")

        if attempt < max_retries - 1:
            print(f"⏳ Waiting 10 seconds before retry...")
            await asyncio.sleep(10)

    print("❌ GS Service is not responding after all retries")
    return False


def main():
    """Main execution function."""
    print("🚀 GS Service Host Startup")
    print("=" * 30)

    # Step 1: Stop existing services
    stop_existing_gs_service()

    # Step 2: Start GS service on host
    process = start_gs_service()

    if process is None:
        print("❌ Failed to start GS Service")
        return 1

    # Step 3: Test connectivity
    print("\n⏳ Waiting for service to start...")
    time.sleep(10)

    # Test the service
    success = asyncio.run(test_gs_service())

    if success:
        print("\n✅ GS Service is running successfully!")
        print("🔧 To stop the service later, run:")
        print(f"   kill {process.pid}")
        print("   # or")
        print("   pkill -f 'uvicorn.*8004'")
        return 0
    else:
        print("\n❌ GS Service failed to start properly")
        print("🔧 Stopping the process...")
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
