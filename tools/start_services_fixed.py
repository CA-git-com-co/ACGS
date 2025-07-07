#!/usr/bin/env python3
"""Start ACGS services with fixed configurations."""

import os
import subprocess
import sys
import time
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def start_service(service_name: str, port: int, working_dir: str) -> bool:
    """Start a single service."""
    try:
        print(f"Starting {service_name} on port {port}...")

        # Set environment variables
        env = os.environ.copy()
        env.update(
            {
                "SERVICE_NAME": service_name,
                "SERVICE_PORT": str(port),
                "LOG_LEVEL": "INFO",
                "ENVIRONMENT": "development",
            }
        )

        # Start service
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            str(port),
        ]

        process = subprocess.Popen(
            cmd,
            cwd=working_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait a moment for startup
        time.sleep(2)

        if process.poll() is None:
            print(f"✅ {service_name} started successfully (PID: {process.pid})")
            return True
        print(f"❌ {service_name} failed to start")
        return False

    except Exception as e:
        print(f"❌ Failed to start {service_name}: {e}")
        return False


def main():
    """Start all services."""
    workspace = Path("/mnt/persist/workspace")

    services = [
        (
            "auth_service",
            8000,
            workspace / "services/platform/authentication/auth_service",
        ),
        ("ac_service", 8001, workspace / "services/core/constitutional-ai/ac_service"),
        (
            "integrity_service",
            8002,
            workspace / "services/platform/integrity/integrity_service",
        ),
        (
            "fv_service",
            8003,
            workspace / "services/core/formal-verification/fv_service",
        ),
        (
            "gs_service",
            8004,
            workspace / "services/core/governance-synthesis/gs_service",
        ),
        (
            "pgc_service",
            8005,
            workspace / "services/core/policy-governance/pgc_service",
        ),
        (
            "ec_service",
            8006,
            workspace / "services/core/evolutionary-computation/ec_service",
        ),
    ]

    started_services = 0
    for service_name, port, working_dir in services:
        if working_dir.exists():
            if start_service(service_name, port, str(working_dir)):
                started_services += 1
        else:
            print(f"⚠️ Service directory not found: {working_dir}")

    print(f"\n📊 Started {started_services}/{len(services)} services")

    if started_services > 0:
        print("\n🔧 To test services, run:")
        print("   python scripts/test_health_endpoints.py")


if __name__ == "__main__":
    main()
