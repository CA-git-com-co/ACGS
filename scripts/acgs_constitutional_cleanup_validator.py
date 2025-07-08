#!/usr/bin/env python3
"""
ACGS Constitutional Cleanup Validator
Constitutional Hash: cdd01ef066bc6cf2

Validates constitutional compliance before and after cleanup operations.
Ensures critical constitutional governance files are preserved.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

# Constitutional compliance requirements
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path("/home/dislove/ACGS-2")

# Critical files that must NEVER be removed
PROTECTED_FILES = {
    "constitutional_compliance_audit_and_fixes.py",
    "fix_constitutional_hashes.py",
    "fix_missing_constitutional_hash.py",
    "step1_constitutional_audit.py",
    "CLAUDE.md",
    "AGENTS.md",
    "GEMINI.md",
    "config/constitutional_compliance.json",
    "docs/training/constitutional_hash_reference.md",
    "tools/acgs_constitutional_compliance_framework.py",
}

# Critical directories that must be preserved
PROTECTED_DIRECTORIES = {
    "services/core",
    "services/shared",
    "config/constitutional_compliance.json",
    "infrastructure/monitoring",
    "docs/constitutional_compliance_validation_framework.md",
}

# Files safe to clean up
SAFE_CLEANUP_PATTERNS = {
    "__pycache__/",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache/",
    ".mypy_cache/",
    "*.tmp",
    "*.temp",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
    "node_modules/",
    "target/debug/",
    "target/release/",
    "build/",
    "dist/",
}


class ConstitutionalCleanupValidator:
    """Validates constitutional compliance during cleanup operations."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.validation_results = {
            "pre_cleanup": {},
            "post_cleanup": {},
            "protected_files_status": {},
            "constitutional_hash_coverage": {},
        }

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for validation operations."""
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        return logging.getLogger(__name__)

    def validate_constitutional_hash_coverage(self) -> dict[str, bool]:
        """Validate constitutional hash presence in critical files."""
        self.logger.info("🔍 Validating constitutional hash coverage...")

        results = {}
        critical_extensions = {".py", ".yml", ".yaml", ".md", ".json"}

        for root, dirs, files in os.walk(REPO_ROOT):
            # Skip certain directories
            dirs[:] = [
                d
                for d in dirs
                if d
                not in {
                    ".git",
                    "__pycache__",
                    ".pytest_cache",
                    "node_modules",
                    ".venv",
                    "venv",
                }
            ]

            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in critical_extensions:
                    relative_path = file_path.relative_to(REPO_ROOT)

                    try:
                        with open(file_path, encoding="utf-8") as f:
                            content = f.read()
                            has_hash = CONSTITUTIONAL_HASH in content
                            results[str(relative_path)] = has_hash

                            if not has_hash and self._is_critical_file(relative_path):
                                self.logger.warning(
                                    "❌ Critical file missing constitutional hash:"
                                    f" {relative_path}"
                                )
                    except (UnicodeDecodeError, PermissionError):
                        continue

        return results

    def _is_critical_file(self, file_path: Path) -> bool:
        """Check if file is critical for constitutional compliance."""
        file_str = str(file_path)

        # Check protected files
        if file_str in PROTECTED_FILES:
            return True

        # Check if in protected directories
        for protected_dir in PROTECTED_DIRECTORIES:
            if file_str.startswith(protected_dir):
                return True

        # Check for constitutional compliance keywords
        critical_keywords = {
            "constitutional",
            "compliance",
            "governance",
            "auth",
            "security",
            "integrity",
        }

        return any(keyword in file_str.lower() for keyword in critical_keywords)

    def validate_protected_files(self) -> dict[str, bool]:
        """Ensure protected files still exist."""
        self.logger.info("🛡️ Validating protected files...")

        results = {}
        for protected_file in PROTECTED_FILES:
            file_path = REPO_ROOT / protected_file
            exists = file_path.exists()
            results[protected_file] = exists

            if not exists:
                self.logger.error(
                    f"❌ CRITICAL: Protected file missing: {protected_file}"
                )
            else:
                self.logger.info(f"✅ Protected file preserved: {protected_file}")

        return results

    def is_safe_to_cleanup(self, file_path: Path) -> bool:
        """Check if file/directory is safe to clean up."""
        file_str = str(file_path.relative_to(REPO_ROOT))

        # Never clean protected files
        if file_str in PROTECTED_FILES:
            return False

        # Never clean protected directories
        for protected_dir in PROTECTED_DIRECTORIES:
            if file_str.startswith(protected_dir):
                return False

        # Check if matches safe cleanup patterns
        for pattern in SAFE_CLEANUP_PATTERNS:
            if pattern.endswith("/"):
                if file_str.endswith(pattern.rstrip("/")):
                    return True
            elif "*" in pattern:
                import fnmatch

                if fnmatch.fnmatch(file_str, pattern):
                    return True
            elif file_str.endswith(pattern):
                return True

        return False

    def run_pre_cleanup_validation(self) -> bool:
        """Run validation before cleanup operations."""
        self.logger.info("🔍 Running pre-cleanup constitutional validation...")

        # Validate constitutional hash coverage
        hash_coverage = self.validate_constitutional_hash_coverage()
        self.validation_results["pre_cleanup"]["hash_coverage"] = hash_coverage

        # Validate protected files
        protected_status = self.validate_protected_files()
        self.validation_results["pre_cleanup"]["protected_files"] = protected_status

        # Check if all critical files have constitutional hash
        critical_files_with_hash = sum(
            1
            for path, has_hash in hash_coverage.items()
            if has_hash and self._is_critical_file(Path(path))
        )

        total_critical_files = sum(
            1 for path in hash_coverage.keys() if self._is_critical_file(Path(path))
        )

        compliance_rate = (
            (critical_files_with_hash / total_critical_files * 100)
            if total_critical_files > 0
            else 100
        )

        self.logger.info(f"📊 Constitutional compliance rate: {compliance_rate:.1f}%")

        # All protected files must exist
        all_protected_exist = all(protected_status.values())

        if not all_protected_exist:
            self.logger.error("❌ CRITICAL: Some protected files are missing!")
            return False

        if compliance_rate < 95:
            self.logger.warning(
                f"⚠️ Constitutional compliance below 95%: {compliance_rate:.1f}%"
            )

        self.logger.info("✅ Pre-cleanup validation completed")
        return True

    def run_post_cleanup_validation(self) -> bool:
        """Run validation after cleanup operations."""
        self.logger.info("🔍 Running post-cleanup constitutional validation...")

        # Re-validate everything
        hash_coverage = self.validate_constitutional_hash_coverage()
        self.validation_results["post_cleanup"]["hash_coverage"] = hash_coverage

        protected_status = self.validate_protected_files()
        self.validation_results["post_cleanup"]["protected_files"] = protected_status

        # Ensure no protected files were accidentally removed
        all_protected_exist = all(protected_status.values())

        if not all_protected_exist:
            self.logger.error(
                "❌ CRITICAL: Protected files were removed during cleanup!"
            )
            return False

        self.logger.info("✅ Post-cleanup validation completed")
        return True

    def save_validation_report(self):
        """Save validation results to file."""
        report_path = REPO_ROOT / "acgs_constitutional_cleanup_validation_report.json"

        self.validation_results["timestamp"] = datetime.now().isoformat()
        self.validation_results["constitutional_hash"] = CONSTITUTIONAL_HASH

        with open(report_path, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        self.logger.info(f"📄 Validation report saved: {report_path}")


def main():
    """Main validation function."""
    validator = ConstitutionalCleanupValidator()

    print("🔧 ACGS Constitutional Cleanup Validator")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository: {REPO_ROOT}")
    print()

    # Run pre-cleanup validation
    if not validator.run_pre_cleanup_validation():
        print("❌ Pre-cleanup validation failed! Cleanup should not proceed.")
        return False

    validator.save_validation_report()
    print("✅ Constitutional validation completed successfully")
    return True


if __name__ == "__main__":
    main()
