#!/usr/bin/env python3
"""
ACGS Production Readiness - Isolated Service Launcher
Starts individual ACGS services with proper isolation and security middleware
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))


def print_status(message):
    print(f"[INFO] {message}")


def print_success(message):
    print(f"[SUCCESS] {message}")


def print_error(message):
    print(f"[ERROR] {message}")


def check_service_health(port, timeout=5):
    """Check if service is responding on health endpoint"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def start_service_process(service_name, port, service_dir, main_module):
    """Start a service process with proper environment isolation"""

    # Set up environment variables
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": f"{PROJECT_ROOT}:{PROJECT_ROOT}/services",
            "DATABASE_URL": "sqlite+aiosqlite:///./acgs_production.db",
            "REDIS_URL": "redis://localhost:6379/0",
            "LOG_LEVEL": "INFO",
            "SERVICE_PORT": str(port),
            "SECRET_KEY": f"acgs-production-{service_name}-{int(time.time())}",
            "CONSTITUTIONAL_HASH": "cdd01ef066bc6cf2",
            "CONSTITUTIONAL_COMPLIANCE_THRESHOLD": "0.95",
            "GOVERNANCE_VALIDATION_ENABLED": "true",
        }
    )

    # Create logs directory for service
    log_dir = service_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # Start service process
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        main_module,
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
        "--log-level",
        "info",
    ]

    print_status(f"Starting {service_name} on port {port}")
    print_status(f"Command: {' '.join(cmd)}")
    print_status(f"Working directory: {service_dir}")

    try:
        process = subprocess.Popen(
            cmd,
            cwd=service_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Wait a moment for startup
        time.sleep(3)

        # Check if process is still running
        if process.poll() is None:
            print_success(f"{service_name} process started (PID: {process.pid})")

            # Wait for health check
            for attempt in range(10):
                if check_service_health(port):
                    print_success(f"{service_name} health check passed")
                    return process
                print_status(
                    f"Waiting for {service_name} health check... (attempt {attempt+1}/10)"
                )
                time.sleep(2)

            print_error(f"{service_name} started but health check failed")
            return process
        else:
            stdout, stderr = process.communicate()
            print_error(f"{service_name} failed to start")
            print_error(f"STDOUT: {stdout}")
            print_error(f"STDERR: {stderr}")
            return None

    except Exception as e:
        print_error(f"Failed to start {service_name}: {e}")
        return None


def main():
    """Main service launcher"""

    # Service configurations
    services = {
        "ac_service": {
            "port": 8002,
            "dir": PROJECT_ROOT / "services/core/constitutional-ai/ac_service",
            "module": "app.main:app",
        },
        "pgc_service": {
            "port": 8003,
            "dir": PROJECT_ROOT / "services/core/policy-governance/pgc_service",
            "module": "app.main:app",
        },
        "gs_service": {
            "port": 8004,
            "dir": PROJECT_ROOT / "services/core/governance-synthesis/gs_service",
            "module": "app.main:app",
        },
        "fv_service": {
            "port": 8005,
            "dir": PROJECT_ROOT / "services/core/formal-verification/fv_service",
            "module": "main:app",
        },
        "ec_service": {
            "port": 8010,
            "dir": PROJECT_ROOT / "services/core/evolutionary-computation",
            "module": "app.main:app",
        },
    }

    if len(sys.argv) < 2:
        print("Usage: python3 start_service_isolated.py <service_name>")
        print("Available services:", list(services.keys()))
        return 1

    service_name = sys.argv[1]
    if service_name not in services:
        print_error(f"Unknown service: {service_name}")
        print("Available services:", list(services.keys()))
        return 1

    config = services[service_name]

    # Check if service directory exists
    if not config["dir"].exists():
        print_error(f"Service directory not found: {config['dir']}")
        return 1

    # Start the service
    process = start_service_process(
        service_name, config["port"], config["dir"], config["module"]
    )

    if process:
        print_success(f"{service_name} started successfully on port {config['port']}")

        # Test constitutional compliance if available
        try:
            response = requests.get(
                f"http://localhost:{config['port']}/health", timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if "constitutional_hash" in data:
                    if data["constitutional_hash"] == "cdd01ef066bc6cf2":
                        print_success(
                            f"{service_name} constitutional compliance validated"
                        )
                    else:
                        print_error(f"{service_name} constitutional hash mismatch")
                else:
                    print_error(f"{service_name} missing constitutional hash")
        except Exception as e:
            print_error(f"Failed to validate {service_name} compliance: {e}")

        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
