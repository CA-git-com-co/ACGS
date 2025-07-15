#!/usr/bin/env python3
"""
Fix imports that use dashes in module paths.
Constitutional Hash: cdd01ef066bc6cf2

This script adds the parent directories to sys.path to enable importing from
directories with dashes in their names.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

def fix_dash_imports_in_file(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix import statements that use dashes in module paths."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixes_applied = []
        
        # Pattern to find imports with dashes
        import_pattern = r'(from\s+|import\s+)(services\.core\.[a-z-]+)'
        
        # Check if file has imports with dashes
        if re.search(r'services\.core\.[a-z-]+', content):
            # Add sys.path manipulation at the top of the file after imports
            lines = content.split('\n')
            
            # Find where to insert sys.path manipulation
            insert_pos = 0
            in_docstring = False
            docstring_delim = None
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Handle docstrings
                if not in_docstring:
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        docstring_delim = '"""' if stripped.startswith('"""') else "'''"
                        if stripped.count(docstring_delim) == 1:
                            in_docstring = True
                        continue
                else:
                    if docstring_delim in line:
                        in_docstring = False
                        continue
                
                # Skip comments and empty lines
                if stripped.startswith('#') or not stripped:
                    continue
                
                # If we find an import statement
                if stripped.startswith('import ') or stripped.startswith('from '):
                    insert_pos = i + 1
                    # Keep looking for more imports
                    continue
                
                # If we find non-import code, we're done
                if insert_pos > 0:
                    break
            
            # Check if sys.path manipulation already exists
            sys_path_exists = 'sys.path.append' in content or 'sys.path.insert' in content
            
            if not sys_path_exists and insert_pos > 0:
                # Add sys.path manipulation
                sys_path_code = [
                    "",
                    "# Add parent directory to path to handle dash-named directories",
                    "import sys",
                    "import os",
                    "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../..'))",
                    ""
                ]
                
                # Insert the code
                for j, code_line in enumerate(sys_path_code):
                    lines.insert(insert_pos + j, code_line)
                
                content = '\n'.join(lines)
                fixes_applied.append("Added sys.path manipulation for dash imports")
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixes_applied
        
        return False, []
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []

def find_test_files(directory: Path) -> List[Path]:
    """Find all test Python files."""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py') and ('test' in file or 'test' in root):
                python_files.append(Path(root) / file)
    
    return python_files

def main():
    """Main function to fix dash imports in test files."""
    project_root = Path.cwd()
    
    print(f"🔧 ACGS-2 Dash Import Fix Script")
    print(f"📁 Project root: {project_root}")
    print(f"🔒 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()
    
    # Target directories
    target_dirs = [
        project_root / "tests",
        project_root / "services" / "core" / "policy-governance" / "pgc_service" / "tests",
        project_root / "services" / "core" / "governance-synthesis" / "gs_service" / "tests",
        project_root / "services" / "core" / "constitutional-ai" / "ac_service" / "tests",
        project_root / "services" / "core" / "formal-verification" / "fv_service" / "tests",
    ]
    
    total_files_processed = 0
    total_files_fixed = 0
    
    for target_dir in target_dirs:
        if not target_dir.exists():
            continue
            
        print(f"🔍 Processing directory: {target_dir}")
        test_files = find_test_files(target_dir)
        
        for file_path in test_files:
            total_files_processed += 1
            was_fixed, fixes = fix_dash_imports_in_file(file_path)
            
            if was_fixed:
                total_files_fixed += 1
                print(f"✅ Fixed {file_path.relative_to(project_root)}")
                for fix in fixes:
                    print(f"   - {fix}")
    
    print()
    print(f"📊 Summary:")
    print(f"   Files processed: {total_files_processed}")
    print(f"   Files fixed: {total_files_fixed}")
    print(f"🔒 Constitutional compliance maintained: {CONSTITUTIONAL_HASH}")

if __name__ == "__main__":
    main()