#!/usr/bin/env python3
"""
ACGS-PGP Import Error Resolution Script
Fixes common import issues across all 7 core services
"""

import os
import re
import sys
from pathlib import Path

def fix_fastapi_middleware_imports(file_path):
    """Fix fastapi.middleware.base imports to use starlette.middleware.base"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix the import statement
        content = content.replace(
            'from fastapi.middleware.base import',
            'from starlette.middleware.base import'
        )
        content = content.replace(
            'fastapi.middleware.base',
            'starlette.middleware.base'
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed FastAPI middleware imports in {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def fix_prometheus_middleware_imports(file_path):
    """Fix prometheus_middleware imports to use correct path"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix prometheus middleware imports
        content = re.sub(
            r"from prometheus_middleware import",
            "from services.shared.prometheus_middleware import",
            content
        )
        content = re.sub(
            r"import prometheus_middleware",
            "import services.shared.prometheus_middleware as prometheus_middleware",
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed Prometheus middleware imports in {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def fix_security_middleware_imports(file_path):
    """Fix security_middleware imports to use correct path"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix security middleware imports
        content = re.sub(
            r"from security_middleware import",
            "from services.shared.security_middleware import",
            content
        )
        content = re.sub(
            r"import security_middleware",
            "import services.shared.security_middleware as security_middleware",
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed security middleware imports in {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def fix_audit_logger_imports(file_path):
    """Fix comprehensive_audit_logger imports to use correct path"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Fix audit logger imports
        content = re.sub(
            r"from comprehensive_audit_logger import",
            "from services.shared.comprehensive_audit_logger import",
            content
        )
        content = re.sub(
            r"import comprehensive_audit_logger",
            "import services.shared.comprehensive_audit_logger as comprehensive_audit_logger",
            content
        )
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Fixed audit logger imports in {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Main function to fix import errors across all services"""
    print("🔧 Starting ACGS-PGP Import Error Resolution...")
    
    # Define service main files
    service_files = [
        "services/platform/authentication/auth_service/app/main.py",
        "services/core/constitutional-ai/ac_service/app/main.py", 
        "services/platform/integrity/integrity_service/app/main.py",
        "services/core/formal-verification/fv_service/main.py",
        "services/core/governance-synthesis/gs_service/app/main.py",
        "services/core/policy-governance/pgc_service/app/main.py",
        "services/core/evolutionary-computation/app/main.py"
    ]
    
    # Fix imports in each service
    for service_file in service_files:
        if os.path.exists(service_file):
            print(f"\n🔧 Fixing imports in {service_file}")
            fix_fastapi_middleware_imports(service_file)
            fix_prometheus_middleware_imports(service_file)
            fix_security_middleware_imports(service_file)
            fix_audit_logger_imports(service_file)
        else:
            print(f"⚠️ Service file not found: {service_file}")
    
    print("\n✅ Import error resolution completed!")

if __name__ == "__main__":
    main()
