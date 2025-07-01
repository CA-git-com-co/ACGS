#!/usr/bin/env python3
"""
Constitutional Compliance Validation Script for ACGS-PGP
Validates constitutional hash integrity and governance compliance.
Used by pre-commit hooks for quick validation.
Constitutional Hash: cdd01ef066bc6cf2
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, List

# Configure minimal logging for pre-commit
logging.basicConfig(level=logging.WARNING)

# Constitutional reference hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalComplianceValidator:
    """Validates constitutional compliance for ACGS-PGP system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations: List[str] = []
        self.warnings: List[str] = []

    def validate_constitutional_hash(self) -> bool:
        """Validate constitutional hash integrity across codebase"""
        try:
            # Quick validation for pre-commit - check critical files only
            critical_files = [
                "services/core/acgs-pgp-v8/src/main.py",
                "services/core/constitutional-ai/ac_service/app/main.py",
            ]
            
            violations_found = False
            
            for file_path in critical_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    if not self._validate_file_hash(full_path):
                        violations_found = True
                        
            # Check for any incorrect hashes in the entire codebase
            violations_found |= self._check_for_incorrect_hashes()
            
            return not violations_found

        except Exception as e:
            self.violations.append(f"Error during validation: {e}")
            return False

    def _validate_file_hash(self, file_path: Path) -> bool:
        """Validate hash in a specific file"""
        try:
            content = file_path.read_text()
            relative_path = file_path.relative_to(self.project_root)
            
            if CONSTITUTIONAL_HASH in content:
                return True
            else:
                # Check for incorrect hash
                hash_pattern = re.compile(
                    r'["\']?(?:constitutional_hash|CONSTITUTIONAL_HASH)["\']?\s*[:=]\s*["\']?([a-f0-9]{16})["\']?',
                    re.IGNORECASE
                )
                
                match = hash_pattern.search(content)
                if match and match.group(1) != CONSTITUTIONAL_HASH:
                    self.violations.append(
                        f"{relative_path} has incorrect constitutional hash: {match.group(1)}"
                    )
                    return False
                else:
                    self.warnings.append(
                        f"{relative_path} missing constitutional hash"
                    )
                    return True  # Warning, not error for pre-commit
                    
        except Exception as e:
            self.violations.append(f"Error reading {file_path}: {e}")
            return False

    def _check_for_incorrect_hashes(self) -> bool:
        """Check for any incorrect constitutional hashes in the codebase"""
        violations_found = False
        hash_pattern = re.compile(
            r'["\']?(?:constitutional_hash|CONSTITUTIONAL_HASH)["\']?\s*[:=]\s*["\']?([a-f0-9]{16})["\']?',
            re.IGNORECASE
        )
        
        # Only check Python files for performance
        for py_file in self.project_root.rglob("*.py"):
            # Skip test files and cache directories
            if any(skip in str(py_file) for skip in ["__pycache__", "test_", "_test", ".git"]):
                continue
                
            try:
                content = py_file.read_text()
                for match in hash_pattern.finditer(content):
                    found_hash = match.group(1)
                    if found_hash != CONSTITUTIONAL_HASH:
                        relative_path = py_file.relative_to(self.project_root)
                        self.violations.append(
                            f"{relative_path} has incorrect constitutional hash: {found_hash}"
                        )
                        violations_found = True
                        break  # Only report first violation per file
                        
            except Exception:
                continue  # Skip files that can't be read
                
        return violations_found

    def run_quick_validation(self) -> bool:
        """Run quick validation suitable for pre-commit hooks"""
        print("⚡ Quick Constitutional Compliance Check...")
        
        # Only do hash validation for pre-commit speed
        hash_valid = self.validate_constitutional_hash()
        
        # Report results
        if self.violations:
            print(f"❌ Found {len(self.violations)} violations:")
            for violation in self.violations:
                print(f"  • {violation}")
                
        if self.warnings:
            print(f"⚠️  Found {len(self.warnings)} warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if hash_valid and not self.violations:
            print("✅ Constitutional compliance check passed!")
            return True
        else:
            print("❌ Constitutional compliance check failed!")
            return False


def main():
    """Main validation function for pre-commit"""
    # Find project root
    project_root = Path.cwd()
    attempts = 0
    while not (project_root / "pyproject.toml").exists() and project_root.parent != project_root and attempts < 10:
        project_root = project_root.parent
        attempts += 1
    
    if not (project_root / "pyproject.toml").exists():
        # Try common locations
        for possible_root in [Path.cwd(), Path.cwd().parent, Path("/home/dislove/ACGS-2")]:
            if (possible_root / "pyproject.toml").exists():
                project_root = possible_root
                break
        else:
            print("❌ Could not find project root (pyproject.toml)")
            sys.exit(1)
    
    validator = ConstitutionalComplianceValidator(project_root)
    
    if validator.run_quick_validation():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()