#!/usr/bin/env python3
"""
Safe Directory Reorganization Script for ACGS-2

This script provides safeguards for directory reorganization operations
to prevent virtual environment corruption and other critical issues.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import re
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Set, Dict, Tuple


class SafeReorganizer:
    """Safely performs directory reorganization with protection measures."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.protected_paths = {
            ".venv", ".git", "__pycache__", "node_modules",
            ".pytest_cache", ".mypy_cache", ".ruff_cache",
            "site-packages", "dist-packages"
        }
        self.dangerous_patterns = [
            r"os\.environ",
            r"sys\.path",
            r"import\s+os",
            r"from\s+os\s+import"
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
    
    def validate_find_replace_operation(self, find_pattern: str, replace_pattern: str) -> Tuple[bool, str]:
        """Validate that a find-replace operation is safe."""
        # Check for dangerous patterns
        dangerous_replacements = [
            ("os.environ", "os.environ"),
            ("os.path", "os.path"),
            ("sys.path", "sys.path"),
            ("import os", "import os"),
        ]
        
        for dangerous_find, dangerous_replace in dangerous_replacements:
            if find_pattern == dangerous_find and replace_pattern == dangerous_replace:
                return False, f"Dangerous replacement detected: {find_pattern} -> {replace_pattern}"
        
        # Check if replacement affects Python imports
        if "import" in find_pattern and "config" in replace_pattern:
            return False, f"Potentially dangerous import replacement: {find_pattern} -> {replace_pattern}"
        
        # Check if replacement affects environment variables
        if "environ" in find_pattern and "config" in replace_pattern:
            return False, f"Environment variable replacement detected: {find_pattern} -> {replace_pattern}"
        
        return True, "Safe replacement"
    
    def scan_for_dangerous_content(self, file_path: Path) -> List[str]:
        """Scan a file for dangerous content patterns."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Check for corruption patterns
                if "os.environ" in content:
                    issues.append("Virtual environment corruption pattern detected")
                
                # Check for malformed imports
                if re.search(r"import\s+osconfig", content):
                    issues.append("Malformed import statement detected")
                
                # Check for broken path references
                if "os.path" in content:
                    issues.append("Broken path reference detected")
                    
        except Exception as e:
            issues.append(f"Failed to scan file: {e}")
        
        return issues
    
    def create_backup(self, backup_name: str = None) -> Path:
        """Create a full project backup before reorganization."""
        if backup_name is None:
            backup_name = f"acgs2_backup_{int(os.time())}"
        
        backup_path = self.project_root.parent / backup_name
        
        print(f"Creating project backup at {backup_path}")
        
        # Copy project excluding large directories
        exclude_patterns = {".venv", ".git", "__pycache__", "node_modules"}
        
        try:
            backup_path.mkdir(exist_ok=True)
            
            for item in self.project_root.iterdir():
                if item.name not in exclude_patterns:
                    if item.is_dir():
                        shutil.copytree(item, backup_path / item.name)
                    else:
                        shutil.copy2(item, backup_path / item.name)
            
            print(f"✅ Backup created successfully at {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Failed to create backup: {e}")
            raise
    
    def safe_find_replace(self, find_pattern: str, replace_pattern: str, 
                         file_extensions: List[str] = None) -> Dict[str, int]:
        """Safely perform find-replace operations with validation."""
        
        if file_extensions is None:
            file_extensions = ['.py', '.md', '.txt', '.yml', '.yaml', '.json']
        
        # Validate the operation
        is_safe, message = self.validate_find_replace_operation(find_pattern, replace_pattern)
        if not is_safe:
            raise ValueError(f"Unsafe operation blocked: {message}")
        
        results = {"files_processed": 0, "replacements_made": 0, "errors": 0}
        
        print(f"Performing safe find-replace: '{find_pattern}' -> '{replace_pattern}'")
        
        for ext in file_extensions:
            for file_path in self.project_root.rglob(f"*{ext}"):
                # Skip protected paths
                if self.is_protected_path(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if find_pattern in content:
                        new_content = content.replace(find_pattern, replace_pattern)
                        
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        results["replacements_made"] += content.count(find_pattern)
                        print(f"  ✅ Updated: {file_path}")
                    
                    results["files_processed"] += 1
                    
                except Exception as e:
                    print(f"  ❌ Error processing {file_path}: {e}")
                    results["errors"] += 1
        
        return results
    
    def validate_project_integrity(self) -> Dict[str, bool]:
        """Validate project integrity after reorganization."""
        checks = {
            "venv_integrity": False,
            "python_imports": False,
            "config_files": False,
            "no_corruption": False
        }
        
        # Check virtual environment
        venv_path = self.project_root / ".venv"
        if venv_path.exists():
            pip_path = venv_path / "bin" / "pip"
            if pip_path.exists():
                try:
                    result = subprocess.run(
                        [str(pip_path), "--version"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    checks["venv_integrity"] = result.returncode == 0
                except Exception:
                    checks["venv_integrity"] = False
        
        # Check for corruption patterns
        corruption_found = False
        for py_file in self.project_root.rglob("*.py"):
            if self.is_protected_path(py_file):
                continue
            
            issues = self.scan_for_dangerous_content(py_file)
            if issues:
                corruption_found = True
                print(f"❌ Issues in {py_file}: {issues}")
        
        checks["no_corruption"] = not corruption_found
        
        # Check Python imports
        try:
            result = subprocess.run(
                [sys.executable, "-c", "import os, sys; print('OK')"],
                capture_output=True,
                text=True,
                timeout=5
            )
            checks["python_imports"] = result.returncode == 0
        except Exception:
            checks["python_imports"] = False
        
        # Check config files
        config_files = ["config/environments/requirements.txt", "config/environments/pyproject.toml", "config/environments/pytest.ini"]
        checks["config_files"] = all(
            (self.project_root / cf).exists() for cf in config_files
        )
        
        return checks


def main():
    """Main function for safe reorganization operations."""
    if len(sys.argv) < 2:
        print("Usage: python safe_reorganization.py <project_root> [command] [args...]")
        print("Commands:")
        print("  validate - Validate project integrity")
        print("  backup - Create project backup")
        print("  find-replace <find> <replace> - Safe find-replace operation")
        sys.exit(1)
    
    project_root = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else "validate"
    
    reorganizer = SafeReorganizer(project_root)
    
    print("🛡️  ACGS-2 Safe Directory Reorganization")
    print("=" * 50)
    print(f"Project Root: {project_root}")
    print(f"Command: {command}")
    print(f"Constitutional Hash: cdd01ef066bc6cf2")
    print()
    
    try:
        if command == "validate":
            checks = reorganizer.validate_project_integrity()
            print("🔍 Project Integrity Validation:")
            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                print(f"  {status} {check}")
            
            all_passed = all(checks.values())
            print(f"\n{'✅' if all_passed else '❌'} Overall Status: {'PASS' if all_passed else 'FAIL'}")
            return 0 if all_passed else 1
        
        elif command == "backup":
            backup_path = reorganizer.create_backup()
            print(f"✅ Backup completed: {backup_path}")
            return 0
        
        elif command == "find-replace":
            if len(sys.argv) < 5:
                print("❌ find-replace requires <find> <replace> arguments")
                return 1
            
            find_pattern = sys.argv[3]
            replace_pattern = sys.argv[4]
            
            results = reorganizer.safe_find_replace(find_pattern, replace_pattern)
            print(f"✅ Find-replace completed:")
            print(f"  Files processed: {results['files_processed']}")
            print(f"  Replacements made: {results['replacements_made']}")
            print(f"  Errors: {results['errors']}")
            return 0
        
        else:
            print(f"❌ Unknown command: {command}")
            return 1
    
    except Exception as e:
        print(f"❌ Operation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
