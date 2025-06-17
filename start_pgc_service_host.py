#!/usr/bin/env python3
"""
PGC Service Host-Based Startup Script
Starts the Policy Governance Compliance service on port 8005
"""

import asyncio
import os
import subprocess
import sys
import time
from pathlib import Path

import aiohttp


def setup_environment():
    """Set up environment variables for PGC service."""
    print("🔧 Setting up environment variables...")

    # Core service URLs
    os.environ["AUTH_SERVICE_URL"] = "http://localhost:8000"
    os.environ["AC_SERVICE_URL"] = "http://localhost:8001"
    os.environ["INTEGRITY_SERVICE_URL"] = "http://localhost:8002"
    os.environ["FV_SERVICE_URL"] = "http://localhost:8003"
    os.environ["GS_SERVICE_URL"] = "http://localhost:8004"
    os.environ["EC_SERVICE_URL"] = "http://localhost:8006"

    # Database configuration
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://acgs_user:acgs_password@localhost:5433/acgs_pgp_db"
    )

    # Security configuration
    os.environ["JWT_SECRET_KEY"] = (
        "acgs-development-secret-key-2024-phase1-infrastructure-stabilization-jwt-token-signing"
    )
    os.environ["CSRF_SECRET_KEY"] = "your_strong_csrf_secret_key_for_pgc_service"

    # Service configuration
    os.environ["ENVIRONMENT"] = "development"
    os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost:3000,http://localhost:3001"
    os.environ["PYTHONPATH"] = (
        "/home/dislove/ACGS-1/services/shared:/home/dislove/ACGS-1/services/core/policy-governance/pgc_service"
    )

    # Policy configuration
    os.environ["POLICY_REFRESH_INTERVAL_SECONDS"] = "300"
    os.environ["OPA_URL"] = "http://localhost:8181"

    print("✅ Environment variables configured")


def kill_existing_process():
    """Kill any existing PGC service process."""
    print("🔄 Checking for existing PGC service processes...")

    try:
        # Kill processes on port 8005
        subprocess.run(["pkill", "-f", "uvicorn.*8005"], check=False)
        subprocess.run(
            ["fuser", "-k", "8005/tcp"], check=False, stderr=subprocess.DEVNULL
        )
        time.sleep(2)
        print("✅ Existing processes terminated")
    except Exception as e:
        print(f"⚠️ Error killing existing processes: {e}")


def start_pgc_service():
    """Start the PGC service on the host."""
    print("🚀 Starting PGC Service on host...")

    # Change to PGC service directory
    pgc_service_dir = Path(
        "/home/dislove/ACGS-1/services/core/policy-governance/pgc_service"
    )

    if not pgc_service_dir.exists():
        print(f"❌ PGC Service directory not found: {pgc_service_dir}")
        return None

    print(f"📁 Working directory: {pgc_service_dir}")

    # Start the service
    cmd = ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8005", "--reload"]

    print(f"🔧 Command: {' '.join(cmd)}")
    print("🌍 Environment variables set:")
    for key, value in os.environ.items():
        if "SERVICE_URL" in key or "DATABASE_URL" in key:
            print(f"  {key}={value}")

    try:
        # Start the process
        process = subprocess.Popen(
            cmd,
            cwd=pgc_service_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=os.environ.copy(),
        )

        print(f"✅ PGC Service started with PID: {process.pid}")

        # Save PID for later management
        pid_file = Path("/home/dislove/ACGS-1/pids/pgc_service.pid")
        pid_file.parent.mkdir(exist_ok=True)
        pid_file.write_text(str(process.pid))

        return process

    except Exception as e:
        print(f"❌ Failed to start PGC service: {e}")
        return None


async def test_pgc_service():
    """Test PGC service connectivity."""
    print("🧪 Testing PGC service connectivity...")

    try:
        async with aiohttp.ClientSession() as session:
            # Test health endpoint
            async with session.get(
                "http://localhost:8005/health", timeout=10
            ) as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(
                        f"✅ PGC Service health check passed: {health_data.get('status', 'unknown')}"
                    )
                    return True
                else:
                    print(f"❌ PGC Service health check failed: HTTP {response.status}")
                    return False

    except Exception as e:
        print(f"❌ PGC Service connectivity test failed: {e}")
        return False


def main():
    """Main execution function."""
    print("🚀 PGC Service Host-Based Startup")
    print("=" * 40)

    # Step 1: Setup environment
    setup_environment()

    # Step 2: Kill existing processes
    kill_existing_process()

    # Step 3: Start PGC service
    process = start_pgc_service()

    if not process:
        print("❌ Failed to start PGC service")
        return 1

    # Step 4: Wait for service to start
    print("\n⏳ Waiting for service to start...")
    time.sleep(15)

    # Step 5: Test the service
    success = asyncio.run(test_pgc_service())

    if success:
        print("\n✅ PGC Service is running successfully!")
        print("🔧 To stop the service later, run:")
        print(f"   kill {process.pid}")
        print("   # or")
        print("   pkill -f 'uvicorn.*8005'")

        # Save log location
        log_file = Path("/home/dislove/ACGS-1/logs/pgc_service.log")
        log_file.parent.mkdir(exist_ok=True)
        print(f"📄 Logs will be available at: {log_file}")

        return 0
    else:
        print("\n❌ PGC Service failed to start properly")
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
