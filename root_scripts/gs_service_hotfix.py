#!/usr/bin/env python3
"""
GS Service Hot-Fix for Dependency Connectivity

This script creates a hot-fix by modifying the GS service health check logic
to use localhost URLs instead of Docker container names.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def apply_gs_service_hotfix():
    """Apply hot-fix to GS Service main.py file."""

    gs_main_path = Path("services/core/governance-synthesis/gs_service/app/main.py")

    if not gs_main_path.exists():
        print(f"❌ GS Service main.py not found at {gs_main_path}")
        return False

    print(f"🔧 Applying hot-fix to {gs_main_path}")

    # Read the current file
    with open(gs_main_path) as f:
        content = f.read()

    # Create backup
    backup_path = gs_main_path.with_suffix(".py.backup")
    with open(backup_path, "w") as f:
        f.write(content)
    print(f"💾 Backup created: {backup_path}")

    # Apply hot-fix: Replace Docker URLs with localhost URLs
    hotfix_replacements = [
        ("http://ac_service:8001", "http://localhost:8001"),
        ("http://integrity_service:8002", "http://localhost:8002"),
        ("http://fv_service:8003", "http://localhost:8003"),
        ("http://pgc_service:8005", "http://localhost:8005"),
        ("http://ec_service:8006", "http://localhost:8006"),
        ("http://auth_service:8000", "http://localhost:8000"),
    ]

    modified_content = content
    changes_made = 0

    for old_url, new_url in hotfix_replacements:
        if old_url in modified_content:
            modified_content = modified_content.replace(old_url, new_url)
            changes_made += 1
            print(f"  ✅ Replaced {old_url} -> {new_url}")

    # Also fix the environment variable defaults
    env_replacements = [
        (
            "'AC_SERVICE_URL', 'http://ac_service:8001'",
            "'AC_SERVICE_URL', 'http://localhost:8001'",
        ),
        (
            "'INTEGRITY_SERVICE_URL', 'http://integrity_service:8002'",
            "'INTEGRITY_SERVICE_URL', 'http://localhost:8002'",
        ),
        (
            "'FV_SERVICE_URL', 'http://fv_service:8003'",
            "'FV_SERVICE_URL', 'http://localhost:8003'",
        ),
        (
            "'PGC_SERVICE_URL', 'http://pgc_service:8005'",
            "'PGC_SERVICE_URL', 'http://localhost:8005'",
        ),
        (
            "'EC_SERVICE_URL', 'http://ec_service:8006'",
            "'EC_SERVICE_URL', 'http://localhost:8006'",
        ),
        (
            "'AUTH_SERVICE_URL', 'http://auth_service:8000'",
            "'AUTH_SERVICE_URL', 'http://localhost:8000'",
        ),
    ]

    for old_env, new_env in env_replacements:
        if old_env in modified_content:
            modified_content = modified_content.replace(old_env, new_env)
            changes_made += 1
            print(
                f"  ✅ Fixed environment default: {old_env.split(',')[0]} -> localhost"
            )

    if changes_made > 0:
        # Write the modified content
        with open(gs_main_path, "w") as f:
            f.write(modified_content)

        print(f"✅ Hot-fix applied successfully! {changes_made} changes made.")
        print("🔄 The service should automatically reload due to --reload flag")
        return True
    print("ℹ️ No changes needed - URLs already use localhost")
    return True


def create_environment_override():
    """Create environment variable override for all services."""

    env_override = """#!/bin/bash
# Environment Variable Override for ACGS-1 Services
# Source this file to set correct service URLs

export AC_SERVICE_URL="http://localhost:8001"
export INTEGRITY_SERVICE_URL="http://localhost:8002"
export FV_SERVICE_URL="http://localhost:8003"
export GS_SERVICE_URL="http://localhost:8004"
export PGC_SERVICE_URL="http://localhost:8005"
export EC_SERVICE_URL="http://localhost:8006"
export AUTH_SERVICE_URL="http://localhost:8000"

export SERVICE_DISCOVERY_ENABLED="true"
export HEALTH_CHECK_TIMEOUT="5.0"
export REQUEST_TIMEOUT="30.0"

echo "✅ ACGS-1 service environment variables set for localhost deployment"
"""

    env_file = "set_service_env.sh"
    with open(env_file, "w") as f:
        f.write(env_override)

    os.chmod(env_file, 0o755)
    print(f"📝 Created environment override: {env_file}")
    return env_file


def main():
    """Main execution function."""
    print("🚀 GS Service Hot-Fix Application")
    print("=" * 40)

    success = True

    # Apply hot-fix to GS Service
    if not apply_gs_service_hotfix():
        success = False

    # Create environment override
    env_file = create_environment_override()

    print("\n📋 SUMMARY")
    print("=" * 15)

    if success:
        print("✅ Hot-fix applied successfully!")
        print("🔄 GS Service should automatically reload with new configuration")
        print("⏳ Wait 10-15 seconds for reload to complete")
        print("\n💡 To verify the fix:")
        print("   curl -s http://localhost:8004/health | jq .")
    else:
        print("❌ Hot-fix application failed")
        print("💡 Manual intervention may be required")

    print(f"\n📄 Environment override available: source {env_file}")

    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
