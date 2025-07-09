#!/usr/bin/env python3
"""
Direct startup script for Integrity Service with proper Python path configuration.
"""

import os
import sys
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def setup_environment():
    """Set up the environment for the integrity service."""
    # Set up Python path
    project_root = Path("/home/dislove/ACGS-1")
    shared_path = project_root / "services" / "shared"

    # Add to Python path
    if str(shared_path) not in sys.path:
        sys.path.insert(0, str(shared_path))

    # Set environment variables
    os.environ["PYTHONPATH"] = f"{shared_path}:{os.environ.get('PYTHONPATH', '')}"
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_db"
    )
    os.environ["REDIS_URL"] = "redis://localhost:6379/0"

    print(f"✅ Python path configured: {sys.path[:3]}")
    print(f"✅ PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")


def start_integrity_service():
    """Start the integrity service directly."""
    setup_environment()

    # Change to service directory
    service_dir = Path(
        "/home/dislove/ACGS-1/services/platform/integrity/integrity_service"
    )
    os.chdir(service_dir)

    print(f"📁 Working directory: {service_dir}")
    print("🚀 Starting Integrity Service...")

    # Import and run the service
    try:
        # Add the service directory to path
        sys.path.insert(0, str(service_dir))

        # Import uvicorn and run
        import uvicorn

        # Run the service
        uvicorn.run(
            "app.main:app", host="0.0.0.0", port=8002, log_level="info", access_log=True
        )

    except Exception as e:
        print(f"❌ Failed to start integrity service: {e}")
        return False

    return True


if __name__ == "__main__":
    success = start_integrity_service()
    if not success:
        sys.exit(1)
