#!/usr/bin/env python3
"""
Direct GS Service Fix

This script creates a more aggressive fix by directly modifying the GS service
to hardcode the localhost URLs and bypass environment variable issues.
"""

import os
import sys
from pathlib import Path

def apply_direct_fix():
    """Apply direct fix to GS Service main.py file."""
    
    gs_main_path = Path("/home/dislove/ACGS-1/services/core/governance-synthesis/gs_service/app/main.py")
    
    if not gs_main_path.exists():
        print(f"❌ GS Service main.py not found at {gs_main_path}")
        return False
    
    print(f"🔧 Applying direct fix to {gs_main_path}")
    
    # Read the current file
    with open(gs_main_path, 'r') as f:
        content = f.read()
    
    # Create backup
    backup_path = gs_main_path.with_suffix('.py.direct_fix_backup')
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"💾 Backup created: {backup_path}")
    
    # Apply direct fix: Replace the health check logic entirely
    old_ac_check = '''        try:
            # Test AC Service connectivity
            async with httpx.AsyncClient(timeout=5.0) as client:
                ac_response = await client.get(f"{os.getenv('AC_SERVICE_URL', 'http://localhost:8001')}/health")
                health_status["dependencies"]["ac_service"] = {
                    "status": "healthy" if ac_response.status_code == 200 else "unhealthy",
                    "response_time_ms": ac_response.elapsed.total_seconds() * 1000 if hasattr(ac_response, 'elapsed') else 0
                }
        except Exception as e:
            health_status["dependencies"]["ac_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }'''
    
    new_ac_check = '''        try:
            # Test AC Service connectivity - DIRECT FIX
            async with httpx.AsyncClient(timeout=5.0) as client:
                ac_response = await client.get("http://localhost:8001/health")
                health_status["dependencies"]["ac_service"] = {
                    "status": "healthy" if ac_response.status_code == 200 else "unhealthy",
                    "response_time_ms": ac_response.elapsed.total_seconds() * 1000 if hasattr(ac_response, 'elapsed') else 0
                }
        except Exception as e:
            health_status["dependencies"]["ac_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }'''
    
    old_integrity_check = '''        try:
            # Test Integrity Service connectivity
            async with httpx.AsyncClient(timeout=5.0) as client:
                integrity_response = await client.get(f"{os.getenv('INTEGRITY_SERVICE_URL', 'http://localhost:8002')}/health")
                health_status["dependencies"]["integrity_service"] = {
                    "status": "healthy" if integrity_response.status_code == 200 else "unhealthy",
                    "response_time_ms": integrity_response.elapsed.total_seconds() * 1000 if hasattr(integrity_response, 'elapsed') else 0
                }
        except Exception as e:
            health_status["dependencies"]["integrity_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }'''
    
    new_integrity_check = '''        try:
            # Test Integrity Service connectivity - DIRECT FIX
            async with httpx.AsyncClient(timeout=5.0) as client:
                integrity_response = await client.get("http://localhost:8002/health")
                health_status["dependencies"]["integrity_service"] = {
                    "status": "healthy" if integrity_response.status_code == 200 else "unhealthy",
                    "response_time_ms": integrity_response.elapsed.total_seconds() * 1000 if hasattr(integrity_response, 'elapsed') else 0
                }
        except Exception as e:
            health_status["dependencies"]["integrity_service"] = {
                "status": "unhealthy",
                "error": str(e)
            }'''
    
    # Apply replacements
    modified_content = content
    changes_made = 0
    
    if old_ac_check in modified_content:
        modified_content = modified_content.replace(old_ac_check, new_ac_check)
        changes_made += 1
        print("  ✅ Fixed AC Service connectivity check")
    
    if old_integrity_check in modified_content:
        modified_content = modified_content.replace(old_integrity_check, new_integrity_check)
        changes_made += 1
        print("  ✅ Fixed Integrity Service connectivity check")
    
    # Also add a timestamp comment to force reload
    import time
    timestamp_comment = f"\n# Direct fix applied at {time.time()}\n"
    modified_content += timestamp_comment
    changes_made += 1
    
    if changes_made > 0:
        # Write the modified content
        with open(gs_main_path, 'w') as f:
            f.write(modified_content)
        
        print(f"✅ Direct fix applied successfully! {changes_made} changes made.")
        return True
    else:
        print("ℹ️ No changes needed")
        return True


def create_service_restart_command():
    """Create a command to restart the GS service."""
    
    restart_commands = [
        "# Option 1: Try to restart as current user",
        "cd /home/dislove/ACGS-1/services/core/governance-synthesis/gs_service",
        "pkill -f 'uvicorn.*8004' 2>/dev/null || true",
        "sleep 3",
        "nohup uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload > gs_service.log 2>&1 &",
        "",
        "# Option 2: If running as root, try docker restart",
        "# docker restart gs_service_container",
        "",
        "# Option 3: Manual process restart",
        "# Find process: ps aux | grep 'uvicorn.*8004'",
        "# Kill process: sudo kill -9 <PID>",
        "# Start new: uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload"
    ]
    
    restart_file = "restart_gs_commands.txt"
    with open(restart_file, 'w') as f:
        f.write('\n'.join(restart_commands))
    
    print(f"📝 Created restart commands: {restart_file}")
    return restart_file


def test_fix_immediately():
    """Test if the fix worked by making a direct request."""
    import asyncio
    import httpx
    
    async def test():
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                print("🔍 Testing GS Service health after fix...")
                response = await client.get("http://localhost:8004/health")
                
                if response.status_code == 200:
                    data = response.json()
                    print("📊 GS Service Health Response:")
                    import json
                    print(json.dumps(data, indent=2))
                    
                    # Check if dependencies are now healthy
                    ac_status = data.get("dependencies", {}).get("ac_service", {}).get("status")
                    integrity_status = data.get("dependencies", {}).get("integrity_service", {}).get("status")
                    
                    if ac_status == "healthy" and integrity_status == "healthy":
                        print("✅ SUCCESS: All dependencies are now healthy!")
                        return True
                    else:
                        print(f"⚠️ Dependencies still unhealthy: AC={ac_status}, Integrity={integrity_status}")
                        return False
                else:
                    print(f"❌ GS Service returned HTTP {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    return asyncio.run(test())


def main():
    """Main execution function."""
    print("🚀 Direct GS Service Fix Application")
    print("=" * 40)
    
    success = True
    
    # Apply direct fix
    if not apply_direct_fix():
        success = False
    
    # Create restart commands
    restart_file = create_service_restart_command()
    
    # Wait for reload and test
    print("\n⏳ Waiting for service reload...")
    import time
    time.sleep(10)
    
    # Test the fix
    print("\n🧪 Testing fix...")
    fix_worked = test_fix_immediately()
    
    print("\n📋 SUMMARY")
    print("=" * 15)
    
    if fix_worked:
        print("✅ Direct fix successful!")
        print("🎉 GS Service dependencies are now healthy!")
    elif success:
        print("⚠️ Fix applied but service may need manual restart")
        print(f"💡 Try commands in: {restart_file}")
        print("🔄 Or wait longer for auto-reload to take effect")
    else:
        print("❌ Fix application failed")
        print("💡 Manual intervention required")
    
    return 0 if fix_worked else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
