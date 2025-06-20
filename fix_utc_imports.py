#!/usr/bin/env python3
"""
Fix timezone.utc import compatibility for Python 3.10
Replace 'from datetime import timezone' with 'from datetime import timezone'
and replace all timezone.utc usage with timezone.utc
"""

import os
import re
from pathlib import Path

def fix_utc_imports_in_file(file_path: Path) -> bool:
    """Fix timezone.utc imports in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Replace the import statement
        content = re.sub(
            r'from datetime import ([^,\n]*,\s*)?timezone.utc([,\s][^,\n]*)?',
            lambda m: f"from datetime import {m.group(1) or ''}timezone{m.group(2) or ''}",
            content
        )
        
        # Replace timezone.utc usage with timezone.utc
        content = re.sub(r'\bUTC\b', 'timezone.utc', content)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"Fixed timezone.utc imports in: {file_path}")
            return True
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix timezone.utc imports in all Python files."""
    project_root = Path('/home/ubuntu/ACGS')
    
    # Files that need timezone.utc import fixes
    files_to_fix = [
        'services/shared/utils.py',
        'scripts/create_tables_direct.py',
        'scripts/validate_mab_metrics_functionality.py',
        'tests/integration/test_cryptographic_integrity_phase3.py',
        'services/core/constitutional-ai/ac_service/app/core/cryptographic_signing.py',
        'tests/unit/test_mab_metrics_endpoint.py',
        'services/platform/integrity/integrity_service/app/services/timestamp_service.py',
        'services/shared/models.py',
        'root_scripts/execute_alphaevolve_next_phase.py',
        'services/platform/integrity/integrity_service/app/api/v1/crypto.py',
        'root_scripts/comprehensive_integration_test_runner.py',
        # Authentication service files
        'services/platform/authentication/auth_service/app/core/api_key_manager.py',
        'services/platform/authentication/auth_service/app/core/intrusion_detection.py',
        'services/platform/authentication/auth_service/app/models/user.py',
        'services/platform/authentication/auth_service/app/core/session_manager.py',
        'services/platform/authentication/auth_service/app/core/oauth.py',
        'services/platform/authentication/auth_service/app/core/security_audit.py',
        'services/platform/authentication/auth_service/app/models/security_event.py'
    ]

    # Also search for all Python files with timezone.utc imports
    print("Searching for additional files with timezone.utc imports...")
    for py_file in project_root.glob("**/*.py"):
        if py_file.exists() and "backup" not in str(py_file):
            try:
                content = py_file.read_text(encoding='utf-8')
                if 'from datetime import' in content and 'timezone.utc' in content:
                    if str(py_file.relative_to(project_root)) not in files_to_fix:
                        files_to_fix.append(str(py_file.relative_to(project_root)))
                        print(f"Found additional file: {py_file.relative_to(project_root)}")
            except Exception:
                pass
    
    fixed_count = 0
    for file_path_str in files_to_fix:
        file_path = project_root / file_path_str
        if file_path.exists():
            if fix_utc_imports_in_file(file_path):
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nFixed timezone.utc imports in {fixed_count} files")

if __name__ == "__main__":
    main()
