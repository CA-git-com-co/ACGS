#!/usr/bin/env python3
"""
Enhanced Corruption Fix Script for ACGS-2

This script fixes the systematic corruption where 'os.environ' was replaced
with 'os.environ' and other patterns throughout the codebase.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict


class EnhancedCorruptionFixer:
    """Fixes systematic corruption in the codebase with comprehensive patterns."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.protected_paths = {".venv", ".git", "__pycache__", "node_modules"}
        
        # Comprehensive corruption patterns to fix
        self.corruption_patterns = [
            # Environment variable patterns
            ("os.environ", "os.environ"),
            ("os.environ", "os.environ"),
            ("os.environ", "os.environ"),
            ("os.environ", "os.environ"),
            
            # Import patterns
            ("import os", "import os"),
            ("from os import", "from os import"),
            
            # Path patterns
            ("os.path", "os.path"),
            ("os.path", "os.path"),
            ("sys.path", "sys.path"),
            ("sys.path", "sys.path"),
            
            # Other common patterns
            ("os.", "os."),
            ("sys.", "sys."),
        ]
    
    def is_protected_path(self, path: Path) -> bool:
        """Check if a path should be protected from modification."""
        try:
            rel_path = path.relative_to(self.project_root)
            path_str = str(rel_path)
            
            for protected in self.protected_paths:
                if protected in path_str:
                    return True
            return False
        except ValueError:
            return False
    
    def fix_file(self, file_path: Path) -> Dict[str, int]:
        """Fix corruption patterns in a single file."""
        results = {"patterns_fixed": 0, "total_replacements": 0}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply all corruption fixes in order of specificity (most specific first)
            for corrupt_pattern, correct_pattern in self.corruption_patterns:
                if corrupt_pattern in content:
                    count = content.count(corrupt_pattern)
                    content = content.replace(corrupt_pattern, correct_pattern)
                    if count > 0:
                        results["patterns_fixed"] += 1
                        results["total_replacements"] += count
                        print(f"  Fixed {count} instances of '{corrupt_pattern}' -> '{correct_pattern}'")
            
            # Write back if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return results
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
        
        return {"patterns_fixed": 0, "total_replacements": 0}
    
    def scan_and_fix_corruption(self) -> Dict[str, int]:
        """Scan the entire project and fix corruption patterns."""
        total_results = {
            "files_processed": 0,
            "files_fixed": 0,
            "patterns_fixed": 0,
            "total_replacements": 0
        }
        
        print("🔧 Scanning and fixing corruption patterns...")
        print()
        
        # Process all text files that might contain corruption
        file_extensions = ['.py', '.md', '.txt', '.yml', '.yaml', '.json', '.sh', '.toml']
        
        for ext in file_extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                if self.is_protected_path(file_path):
                    continue
                
                total_results["files_processed"] += 1
                
                # Check if file has corruption
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    has_corruption = any(
                        corrupt_pattern in content 
                        for corrupt_pattern, _ in self.corruption_patterns
                    )
                    
                    if has_corruption:
                        print(f"🔧 Fixing: {file_path}")
                        file_results = self.fix_file(file_path)
                        
                        if file_results["patterns_fixed"] > 0:
                            total_results["files_fixed"] += 1
                            total_results["patterns_fixed"] += file_results["patterns_fixed"]
                            total_results["total_replacements"] += file_results["total_replacements"]
                        
                except Exception as e:
                    print(f"❌ Error scanning {file_path}: {e}")
        
        return total_results
    
    def validate_fixes(self) -> bool:
        """Validate that corruption has been fixed."""
        print("\n🔍 Validating fixes...")
        
        corruption_found = False
        
        for file_path in self.project_root.rglob("*.py"):
            if self.is_protected_path(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for corrupt_pattern, _ in self.corruption_patterns:
                    if corrupt_pattern in content:
                        print(f"❌ Still corrupted: {file_path} contains '{corrupt_pattern}'")
                        corruption_found = True
                        break
                        
            except Exception:
                continue
        
        if not corruption_found:
            print("✅ No corruption patterns found - fixes successful!")
        
        return not corruption_found


def main():
    """Main function to fix corruption."""
    if len(sys.argv) != 2:
        print("Usage: python fix_corruption_v2.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    fixer = EnhancedCorruptionFixer(project_root)
    
    print("🛠️  ACGS-2 Enhanced Corruption Fix Tool")
    print("=" * 50)
    print(f"Project Root: {project_root}")
    print(f"Constitutional Hash: cdd01ef066bc6cf2")
    print()
    
    # Scan and fix corruption
    results = fixer.scan_and_fix_corruption()
    
    # Validate fixes
    validation_passed = fixer.validate_fixes()
    
    # Summary
    print("\n" + "=" * 50)
    print("🔍 Fix Summary:")
    print(f"- Files processed: {results['files_processed']}")
    print(f"- Files fixed: {results['files_fixed']}")
    print(f"- Pattern types fixed: {results['patterns_fixed']}")
    print(f"- Total replacements: {results['total_replacements']}")
    print(f"- Validation: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
    print(f"- Constitutional Hash: cdd01ef066bc6cf2")
    
    return 0 if validation_passed else 1


if __name__ == "__main__":
    sys.exit(main())
