#!/usr/bin/env python3
"""
ACGS-1 Production Environment Setup Script

This script orchestrates the complete setup of a production environment
for the ACGS-1 system, including all services, security configurations,
monitoring, and backup systems.
"""

import logging
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


def run_script(script_path, description):
    """Run a setup script and handle errors."""
    logger.info(f"Running: {description}")
    try:
        if script_path.suffix == ".py":
            subprocess.run([sys.executable, str(script_path)], check=True)
        else:
            subprocess.run(["bash", str(script_path)], check=True)
        logger.info(f"✅ Completed: {description}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed: {description} - {e}")
        return False


def main():
    """Main function to orchestrate production setup."""
    logger.info("🚀 Starting ACGS-1 Production Environment Setup")

    # Create setup directory path
    setup_dir = PROJECT_ROOT / "scripts" / "setup"

    # Define setup steps with their scripts and descriptions
    setup_steps = [
        (setup_dir / "setup_production_auth.py", "Authentication Service Setup"),
        (setup_dir / "setup_redis_infrastructure.py", "Redis Infrastructure Setup"),
        (setup_dir / "setup_monitoring_alerting.py", "Monitoring and Alerting Setup"),
        (
            setup_dir / "setup_backup_disaster_recovery.py",
            "Backup and Disaster Recovery Setup",
        ),
        (setup_dir / "setup_mab_monitoring.py", "MAB Performance Monitoring Setup"),
        (
            PROJECT_ROOT / "scripts" / "generate_secure_env.py",
            "Secure Environment Configuration",
        ),
        (
            PROJECT_ROOT / "scripts" / "deploy_advanced_caching.sh",
            "Advanced Caching Deployment",
        ),
    ]

    # Run each setup step
    success_count = 0
    for script_path, description in setup_steps:
        if run_script(script_path, description):
            success_count += 1

    # Report results
    total_steps = len(setup_steps)
    logger.info(f"Setup completed: {success_count}/{total_steps} steps successful")

    if success_count == total_steps:
        logger.info("🎉 Production environment setup completed successfully!")
        return 0
    logger.warning(
        f"⚠️ Production environment setup completed with {total_steps - success_count} failures"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
