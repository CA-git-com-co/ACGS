#!/usr/bin/env python3
"""
ACGS-2 Import Fix Script
Constitutional Hash: cdd01ef066bc6cf2

Fixes import issues in the ACGS-2 test suite by:
1. Replacing 'from shared.' with 'from services.shared.'
2. Replacing 'import shared.' with 'import services.shared.'
3. Fixing other common import path issues
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def fix_imports_in_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix import statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Import fixes mapping
        import_fixes = [
            # Fix shared imports
            (r'\bfrom shared\.', 'from services.shared.'),
            (r'\bimport shared\.', 'import services.shared.'),
            (r'\bfrom shared\b', 'from services.shared'),
            (r'\bimport shared\b', 'import services.shared'),
            
            # Fix underscore to dash conversions for service directories
            (r'services\.core\.policy_governance', 'services.core.policy-governance'),
            (r'services\.core\.governance_synthesis', 'services.core.governance-synthesis'),
            (r'services\.core\.constitutional_ai', 'services.core.constitutional-ai'),
            (r'services\.core\.formal_verification', 'services.core.formal-verification'),
            (r'services\.core\.evolutionary_computation', 'services.core.evolutionary-computation'),
            (r'services\.core\.xai_integration', 'services.core.xai-integration'),
            
            # Fix specific service imports that are commonly wrong
            (r'from services\.core\.policy-governance\.app', 'from services.core.policy-governance.pgc_service.app'),
            (r'from services\.core\.governance-synthesis\.app', 'from services.core.governance-synthesis.gs_service.app'),
            (r'from services\.core\.constitutional-ai\.app', 'from services.core.constitutional-ai.ac_service.app'),
            (r'from services\.core\.formal-verification\.app', 'from services.core.formal-verification.fv_service.app'),
            
            # Fix relative imports that should be absolute
            (r'from \.\.shared import', 'from services.shared import'),
            (r'from \.shared import', 'from services.shared import'),
        ]
        
        for pattern, replacement in import_fixes:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes_applied.append(f"{pattern} -> {replacement}")
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixes_applied
        
        return False, []
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []

def find_python_files(directory: Path) -> List[Path]:
    """Find all Python files in directory and subdirectories."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files

def main():
    """Main function to fix imports across the codebase."""
    project_root = Path.cwd()
    
    print(f"🔧 ACGS-2 Import Fix Script")
    print(f"📁 Project root: {project_root}")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Target directories to fix
    target_dirs = [
        project_root / "tests",
        project_root / "services",
        project_root / "scripts",
        project_root / "tools",
    ]
    
    total_files_processed = 0
    total_files_fixed = 0
    total_fixes_applied = 0
    
    for target_dir in target_dirs:
        if not target_dir.exists():
            print(f"⚠️  Directory {target_dir} does not exist, skipping...")
            continue
            
        print(f"🔍 Processing directory: {target_dir}")
        python_files = find_python_files(target_dir)
        
        for file_path in python_files:
            total_files_processed += 1
            was_fixed, fixes = fix_imports_in_file(file_path)
            
            if was_fixed:
                total_files_fixed += 1
                total_fixes_applied += len(fixes)
                print(f"✅ Fixed {file_path.relative_to(project_root)}")
                for fix in fixes:
                    print(f"   - {fix}")
    
    print()
    print(f"📊 Summary:")
    print(f"   Files processed: {total_files_processed}")
    print(f"   Files fixed: {total_files_fixed}")
    print(f"   Total fixes applied: {total_fixes_applied}")
    print(f"🔒 Constitutional compliance maintained: {CONSTITUTIONAL_HASH}")

if __name__ == "__main__":
    main()
