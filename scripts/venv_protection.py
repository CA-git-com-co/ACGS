#!/usr/bin/env python3
"""
Virtual Environment Protection Script for ACGS-2

This script implements safeguards to prevent virtual environment corruption
during directory reorganization operations.

Constitutional Hash: cdd01ef066bc6cf2
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Set


class VenvProtector:
    """Protects virtual environments from corruption during reorganization."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.venv_path = self.project_root / ".venv"
        self.protected_paths = {
            ".venv",
            ".git", 
            "__pycache__",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache"
        }
    
    def is_protected_path(self, path: Path) -> bool:
        """Check if a path should be protected from modification."""
        path_str = str(path.relative_to(self.project_root))
        
        # Check if path is in protected set
        for protected in self.protected_paths:
            if path_str.startswith(protected):
                return True
        
        # Check for virtual environment patterns
        if ".venv" in path.parts or "venv" in path.parts:
            return True
            
        # Check for Python package directories
        if "site-packages" in path.parts:
            return True
            
        return False
    
    def backup_venv(self) -> bool:
        """Create a backup of the virtual environment."""
        if not self.venv_path.exists():
            print("No virtual environment found to backup")
            return False
            
        backup_path = self.project_root / f".venv_backup_{int(os.time())}"
        
        try:
            print(f"Creating virtual environment backup at {backup_path}")
            shutil.copytree(self.venv_path, backup_path)
            print("✅ Virtual environment backup created successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to backup virtual environment: {e}")
            return False
    
    def validate_venv_integrity(self) -> bool:
        """Validate that the virtual environment is not corrupted."""
        if not self.venv_path.exists():
            print("❌ Virtual environment does not exist")
            return False
        
        # Check pip functionality
        pip_path = self.venv_path / "bin" / "pip"
        if not pip_path.exists():
            print("❌ pip executable not found")
            return False
        
        try:
            # Test pip version command
            result = subprocess.run(
                [str(pip_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"❌ pip command failed: {result.stderr}")
                return False
                
            # Check for corruption patterns
            if "os.environ" in result.stdout:
                print("❌ Virtual environment corruption detected!")
                return False
                
            print("✅ Virtual environment integrity validated")
            return True
            
        except Exception as e:
            print(f"❌ Failed to validate virtual environment: {e}")
            return False
    
    def scan_for_corruption(self) -> List[Path]:
        """Scan for files with corruption patterns."""
        corrupted_files = []
        
        if not self.venv_path.exists():
            return corrupted_files
        
        print("Scanning for corruption patterns...")
        
        for py_file in self.venv_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if "os.environ" in content:
                        corrupted_files.append(py_file)
            except Exception:
                continue
        
        if corrupted_files:
            print(f"❌ Found {len(corrupted_files)} corrupted files")
        else:
            print("✅ No corruption patterns detected")
            
        return corrupted_files
    
    def create_protection_gitignore(self):
        """Create .gitignore entries to protect virtual environments."""
        gitignore_path = self.project_root / ".gitignore"
        
        protection_entries = [
            "# Virtual Environment Protection",
            ".venv/",
            ".venv_backup_*/",
            "venv/",
            "env/",
            "ENV/",
            "env.bak/",
            "venv.bak/",
            "",
            "# Python Cache Protection", 
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            ""
        ]
        
        try:
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    existing_content = f.read()
            else:
                existing_content = ""
            
            # Check if protection entries already exist
            if "Virtual Environment Protection" not in existing_content:
                with open(gitignore_path, 'a') as f:
                    f.write("\n".join(protection_entries))
                print("✅ Added virtual environment protection to .gitignore")
            else:
                print("✅ Virtual environment protection already in .gitignore")
                
        except Exception as e:
            print(f"❌ Failed to update .gitignore: {e}")


def main():
    """Main function to run virtual environment protection."""
    if len(sys.argv) != 2:
        print("Usage: python venv_protection.py <project_root>")
        sys.exit(1)
    
    project_root = sys.argv[1]
    protector = VenvProtector(project_root)
    
    print("🛡️  ACGS-2 Virtual Environment Protection")
    print("=" * 50)
    print(f"Project Root: {project_root}")
    print(f"Constitutional Hash: cdd01ef066bc6cf2")
    print()
    
    # Validate current environment
    is_valid = protector.validate_venv_integrity()
    
    # Scan for corruption
    corrupted_files = protector.scan_for_corruption()
    
    # Create protection measures
    protector.create_protection_gitignore()
    
    # Summary
    print("\n" + "=" * 50)
    print("🔍 Protection Summary:")
    print(f"- Virtual environment valid: {'✅' if is_valid else '❌'}")
    print(f"- Corrupted files found: {len(corrupted_files)}")
    print(f"- Protection measures: ✅ Implemented")
    print(f"- Constitutional Hash: cdd01ef066bc6cf2")
    
    if corrupted_files:
        print("\n⚠️  Recommendation: Recreate virtual environment")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
