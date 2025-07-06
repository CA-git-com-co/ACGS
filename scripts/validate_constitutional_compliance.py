#!/usr/bin/env python3
"""
Constitutional Compliance Validation Script

Validates that all ACGS components maintain constitutional compliance:
- Constitutional hash presence in all required files
- Constitutional compliance validation in all service responses
- Audit trail completeness for constitutional decisions
- HITL oversight integration for high-uncertainty decisions

Constitutional Hash: cdd01ef066bc6cf2
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import subprocess

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# File patterns that must contain constitutional hash
REQUIRED_PATTERNS = {
    "python_services": {
        "pattern": "services/**/*.py",
        "required": True,
        "description": "Python service files"
    },
    "test_files": {
        "pattern": "tests/**/*.py",
        "required": True,
        "description": "Test files"
    },
    "configuration": {
        "pattern": "**/*.{json,yaml,yml}",
        "required": True,
        "description": "Configuration files"
    },
    "documentation": {
        "pattern": "docs/**/*.md",
        "required": True,
        "description": "Documentation files"
    },
    "api_specs": {
        "pattern": "docs/api/**/*.{yaml,yml,json}",
        "required": True,
        "description": "API specification files"
    },
    "docker_files": {
        "pattern": "**/Dockerfile*",
        "required": False,
        "description": "Docker files"
    },
    "scripts": {
        "pattern": "scripts/**/*.py",
        "required": True,
        "description": "Script files"
    }
}

# Constitutional principles that must be validated
CONSTITUTIONAL_PRINCIPLES = [
    "safety_first",
    "operational_transparency",
    "user_consent",
    "data_privacy",
    "resource_constraints",
    "operation_reversibility",
    "least_privilege",
    "constitutional_compliance"
]


class ConstitutionalComplianceValidator:
    """Validates constitutional compliance across ACGS codebase."""
    
    def __init__(self, constitutional_hash: str, base_path: Path = None):
        self.constitutional_hash = constitutional_hash
        self.base_path = base_path or Path(".")
        self.violations = []
        self.warnings = []
        self.coverage_stats = {}
        
    def validate_compliance(self, coverage_target: float = 100.0) -> bool:
        """Validate constitutional compliance across the codebase."""
        print(f"⚖️  ACGS Constitutional Compliance Validation")
        print(f"📋 Constitutional Hash: {self.constitutional_hash}")
        print(f"🎯 Coverage Target: {coverage_target}%")
        print("=" * 60)
        
        # Validate hash presence in required files
        self._validate_hash_presence()
        
        # Validate constitutional principles implementation
        self._validate_constitutional_principles()
        
        # Validate service responses include constitutional hash
        self._validate_service_responses()
        
        # Validate audit trail completeness
        self._validate_audit_trail()
        
        # Calculate coverage statistics
        self._calculate_coverage_stats()
        
        # Generate compliance report
        return self._generate_compliance_report(coverage_target)
    
    def _validate_hash_presence(self):
        """Validate constitutional hash presence in required files."""
        print("🔍 Validating Constitutional Hash Presence")
        print("-" * 40)
        
        for pattern_name, pattern_config in REQUIRED_PATTERNS.items():
            pattern = pattern_config["pattern"]
            required = pattern_config["required"]
            description = pattern_config["description"]
            
            print(f"  📁 Checking {description}...")
            
            # Find files matching pattern
            files = []
            if pattern == "**/*.{json,yaml,yml}":
                # Handle multiple extensions for configuration files
                files.extend(self.base_path.glob("**/*.json"))
                files.extend(self.base_path.glob("**/*.yaml"))
                files.extend(self.base_path.glob("**/*.yml"))
            elif pattern == "docs/api/**/*.{yaml,yml,json}":
                # Handle multiple extensions for API specs
                files.extend(self.base_path.glob("docs/api/**/*.yaml"))
                files.extend(self.base_path.glob("docs/api/**/*.yml"))
                files.extend(self.base_path.glob("docs/api/**/*.json"))
            else:
                files = list(self.base_path.glob(pattern))
            
            if not files and required:
                self.violations.append(f"No files found for required pattern: {pattern}")
                print(f"    ❌ No files found")
                continue
            
            # Check each file for constitutional hash
            files_with_hash = 0
            total_files = len(files)
            
            for file_path in files:
                if self._file_contains_hash(file_path):
                    files_with_hash += 1
                elif required:
                    self.violations.append(
                        f"Constitutional hash missing in required file: {file_path}"
                    )
            
            coverage = (files_with_hash / total_files * 100) if total_files > 0 else 0
            self.coverage_stats[pattern_name] = {
                "files_with_hash": files_with_hash,
                "total_files": total_files,
                "coverage_percent": coverage
            }
            
            if coverage >= 90:
                print(f"    ✅ {files_with_hash}/{total_files} files ({coverage:.1f}%)")
            elif coverage >= 70:
                print(f"    ⚠️  {files_with_hash}/{total_files} files ({coverage:.1f}%)")
                self.warnings.append(f"Low coverage in {description}: {coverage:.1f}%")
            else:
                print(f"    ❌ {files_with_hash}/{total_files} files ({coverage:.1f}%)")
                if required:
                    self.violations.append(f"Insufficient coverage in {description}: {coverage:.1f}%")
    
    def _validate_constitutional_principles(self):
        """Validate implementation of constitutional principles."""
        print("\n📜 Validating Constitutional Principles Implementation")
        print("-" * 50)
        
        principles_found = set()
        
        # Search for constitutional principles in code
        for file_path in self.base_path.glob("services/**/*.py"):
            content = self._read_file_safe(file_path)
            if content:
                for principle in CONSTITUTIONAL_PRINCIPLES:
                    if principle in content.lower():
                        principles_found.add(principle)
        
        # Check for missing principles
        missing_principles = set(CONSTITUTIONAL_PRINCIPLES) - principles_found
        
        for principle in CONSTITUTIONAL_PRINCIPLES:
            if principle in principles_found:
                print(f"  ✅ {principle}")
            else:
                print(f"  ❌ {principle}")
                self.violations.append(f"Constitutional principle not implemented: {principle}")
        
        if missing_principles:
            self.violations.append(
                f"Missing constitutional principles: {', '.join(missing_principles)}"
            )
    
    def _validate_service_responses(self):
        """Validate that service responses include constitutional hash."""
        print("\n🔗 Validating Service Response Compliance")
        print("-" * 40)
        
        # Look for response models and schemas
        response_files = list(self.base_path.glob("services/**/models/*.py"))
        response_files.extend(self.base_path.glob("services/**/schemas/*.py"))
        
        compliant_responses = 0
        total_responses = 0
        
        for file_path in response_files:
            content = self._read_file_safe(file_path)
            if content and ("response" in content.lower() or "schema" in content.lower()):
                total_responses += 1
                if "constitutional_hash" in content.lower():
                    compliant_responses += 1
                else:
                    self.warnings.append(
                        f"Response model may be missing constitutional_hash: {file_path}"
                    )
        
        if total_responses > 0:
            coverage = compliant_responses / total_responses * 100
            print(f"  📊 Response compliance: {compliant_responses}/{total_responses} ({coverage:.1f}%)")
            
            if coverage < 90:
                self.violations.append(
                    f"Low response compliance coverage: {coverage:.1f}%"
                )
        else:
            self.warnings.append("No response models found for validation")
    
    def _validate_audit_trail(self):
        """Validate audit trail completeness."""
        print("\n📋 Validating Audit Trail Implementation")
        print("-" * 40)
        
        # Look for audit/logging implementations
        audit_patterns = [
            "audit",
            "logging",
            "log_",
            "track_",
            "record_"
        ]
        
        audit_implementations = 0
        
        for file_path in self.base_path.glob("services/**/*.py"):
            content = self._read_file_safe(file_path)
            if content:
                for pattern in audit_patterns:
                    if pattern in content.lower():
                        audit_implementations += 1
                        break
        
        print(f"  📝 Audit implementations found: {audit_implementations}")
        
        if audit_implementations < 5:  # Minimum expected audit implementations
            self.warnings.append(
                f"Limited audit trail implementations found: {audit_implementations}"
            )
    
    def _file_contains_hash(self, file_path: Path) -> bool:
        """Check if file contains the constitutional hash."""
        content = self._read_file_safe(file_path)
        return content and self.constitutional_hash in content
    
    def _read_file_safe(self, file_path: Path) -> str:
        """Safely read file content."""
        try:
            # Skip directories
            if file_path.is_dir():
                return ""
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except (UnicodeDecodeError, PermissionError, FileNotFoundError, IsADirectoryError):
            return ""
    
    def _calculate_coverage_stats(self):
        """Calculate overall coverage statistics."""
        total_files = sum(stats["total_files"] for stats in self.coverage_stats.values())
        files_with_hash = sum(stats["files_with_hash"] for stats in self.coverage_stats.values())
        
        self.overall_coverage = (files_with_hash / total_files * 100) if total_files > 0 else 0
    
    def _generate_compliance_report(self, coverage_target: float) -> bool:
        """Generate constitutional compliance report."""
        print("\n" + "=" * 60)
        print("📊 Constitutional Compliance Report")
        print("=" * 60)
        
        # Overall coverage
        print(f"📈 Overall Coverage: {self.overall_coverage:.1f}% (target: {coverage_target}%)")
        
        # Coverage by category
        print("\n📋 Coverage by Category:")
        for category, stats in self.coverage_stats.items():
            coverage = stats["coverage_percent"]
            files_with_hash = stats["files_with_hash"]
            total_files = stats["total_files"]
            
            status = "✅" if coverage >= 90 else "⚠️" if coverage >= 70 else "❌"
            print(f"  {status} {category}: {files_with_hash}/{total_files} ({coverage:.1f}%)")
        
        # Violations
        if self.violations:
            print(f"\n❌ {len(self.violations)} Constitutional Violations:")
            for i, violation in enumerate(self.violations, 1):
                print(f"  {i}. {violation}")
        
        # Warnings
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
        
        # Constitutional hash validation
        print(f"\n🔐 Constitutional Hash: {self.constitutional_hash}")
        
        # Success criteria
        success = (
            len(self.violations) == 0 and
            self.overall_coverage >= coverage_target
        )
        
        if success:
            print("\n🎉 Constitutional compliance validation passed!")
        else:
            print("\n❌ Constitutional compliance validation failed!")
        
        return success


def main():
    """Main entry point for constitutional compliance validation."""
    parser = argparse.ArgumentParser(description="Validate ACGS constitutional compliance")
    parser.add_argument("--hash", default=CONSTITUTIONAL_HASH, help="Constitutional hash to validate")
    parser.add_argument("--coverage-target", type=float, default=100.0, help="Coverage target percentage")
    parser.add_argument("--base-path", default=".", help="Base path for validation")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Validate constitutional compliance
    validator = ConstitutionalComplianceValidator(
        constitutional_hash=args.hash,
        base_path=Path(args.base_path)
    )
    
    success = validator.validate_compliance(args.coverage_target)
    
    if success:
        print("\n🎉 Constitutional compliance validation passed!")
        sys.exit(0)
    else:
        print("\n❌ Constitutional compliance validation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
