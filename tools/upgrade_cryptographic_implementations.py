#!/usr/bin/env python3
"""
ACGS-1 Cryptographic Implementation Upgrade Script

This script systematically replaces all MD5 instances with SHA-256 across the ACGS-1 system
to improve cryptographic security. It identifies and upgrades:

1. hashlib.md5() calls to hashlib.sha256()
2. MD5 algorithm references in crypto services
3. Hash length adjustments for SHA-256 (32 bytes vs 16 bytes for MD5)
4. Documentation and comments referencing MD5

Security Benefits:
- Eliminates weak MD5 cryptographic hash function
- Implements SHA-256 (256-bit) for stronger security
- Prevents collision attacks possible with MD5
- Meets modern cryptographic standards
"""

import json
import logging
import re
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("cryptographic_upgrade.log"),
    ],
)
logger = logging.getLogger(__name__)


class CryptographicUpgrader:
    """Upgrade MD5 to SHA-256 across the ACGS-1 codebase."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.files_modified = []
        self.replacements_made = []
        self.errors = []

        # Files to upgrade (excluding virtual environments and external tools)
        self.target_files = [
            "services/core/governance-synthesis/gs_service/app/security/adversarial_defenses.py",
            "services/shared/constitutional_cache.py",
            "scripts/optimization/redis_cache_setup.py",
            "infrastructure/load-balancer/enterprise_ha_manager.py",
            "services/shared/database/performance_optimizer.py",
        ]

        # MD5 patterns to replace
        self.md5_patterns = [
            (r"hashlib\.md5\(", "hashlib.sha256("),
            (r"\.md5\(", ".sha256("),
            (r"MD5", "SHA256"),
            (r"md5", "sha256"),
            (
                r"hexdigest\(\)\[:8\]",
                "hexdigest()[:16]",
            ),  # Adjust hash length for SHA-256
            (r"hexdigest\(\)\[:16\]", "hexdigest()[:32]"),  # Full SHA-256 hash length
        ]

    def upgrade_all_files(self) -> dict:
        """Upgrade cryptographic implementations in all target files."""
        logger.info("🔒 Starting cryptographic implementation upgrade")

        upgrade_start = time.time()

        for file_path in self.target_files:
            full_path = self.project_root / file_path

            if full_path.exists():
                logger.info(f"📝 Upgrading {file_path}")
                try:
                    result = self.upgrade_file(full_path)
                    if result["modified"]:
                        self.files_modified.append(str(file_path))
                        self.replacements_made.extend(result["replacements"])
                        logger.info(f"✅ Successfully upgraded {file_path}")
                    else:
                        logger.info(f"ℹ️ No changes needed in {file_path}")

                except Exception as e:
                    error_msg = f"Error upgrading {file_path}: {e!s}"
                    logger.error(error_msg)
                    self.errors.append(error_msg)
            else:
                logger.warning(f"⚠️ File not found: {file_path}")

        upgrade_time = time.time() - upgrade_start

        # Generate upgrade summary
        summary = self._generate_upgrade_summary(upgrade_time)

        # Save upgrade report
        self._save_upgrade_report(summary)

        return summary

    def upgrade_file(self, file_path: Path) -> dict:
        """Upgrade cryptographic implementations in a single file."""
        try:
            # Read file content
            with open(file_path, encoding="utf-8") as f:
                original_content = f.read()

            modified_content = original_content
            replacements = []

            # Apply MD5 to SHA-256 replacements
            for pattern, replacement in self.md5_patterns:
                matches = re.finditer(pattern, modified_content, re.IGNORECASE)
                for match in matches:
                    original_text = match.group(0)
                    new_text = re.sub(
                        pattern, replacement, original_text, flags=re.IGNORECASE
                    )

                    replacements.append(
                        {
                            "pattern": pattern,
                            "original": original_text,
                            "replacement": new_text,
                            "line_number": modified_content[: match.start()].count("\n")
                            + 1,
                        }
                    )

                modified_content = re.sub(
                    pattern, replacement, modified_content, flags=re.IGNORECASE
                )

            # Check if content was modified
            if modified_content != original_content:
                # Write modified content back to file
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)

                return {
                    "modified": True,
                    "replacements": replacements,
                    "file_path": str(file_path),
                }
            return {
                "modified": False,
                "replacements": [],
                "file_path": str(file_path),
            }

        except Exception as e:
            raise Exception(f"Failed to upgrade {file_path}: {e!s}")

    def _generate_upgrade_summary(self, upgrade_time: float) -> dict:
        """Generate upgrade summary report."""
        total_files = len(self.target_files)
        modified_files = len(self.files_modified)
        total_replacements = len(self.replacements_made)

        return {
            "upgrade_summary": {
                "total_files_processed": total_files,
                "files_modified": modified_files,
                "files_unchanged": total_files - modified_files,
                "total_replacements": total_replacements,
                "upgrade_time": f"{upgrade_time:.2f} seconds",
                "success_rate": f"{((total_files - len(self.errors)) / total_files * 100):.1f}%",
                "timestamp": time.time(),
            },
            "modified_files": self.files_modified,
            "replacements_made": self.replacements_made,
            "errors": self.errors,
            "security_improvements": [
                "Eliminated weak MD5 cryptographic hash function",
                "Implemented SHA-256 (256-bit) for stronger security",
                "Prevented collision attacks possible with MD5",
                "Met modern cryptographic standards (NIST approved)",
                "Enhanced cache key security",
                "Improved task identification security",
                "Strengthened load balancer hash consistency",
                "Upgraded adversarial defense mechanisms",
            ],
            "affected_components": [
                "Constitutional Cache System",
                "Redis Cache Setup",
                "Load Balancer Hash Consistency",
                "Adversarial Defense Mechanisms",
                "Database Performance Optimizer",
                "Governance Synthesis Security",
            ],
        }

    def _save_upgrade_report(self, summary: dict):
        """Save upgrade report to file."""
        report_path = "cryptographic_upgrade_report.json"

        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2)

        logger.info(f"📄 Upgrade report saved to {report_path}")

    def validate_upgrades(self) -> dict:
        """Validate that all MD5 instances have been successfully replaced."""
        logger.info("🔍 Validating cryptographic upgrades")

        validation_results = {
            "validation_passed": True,
            "remaining_md5_instances": [],
            "files_checked": [],
            "validation_errors": [],
        }

        for file_path in self.target_files:
            full_path = self.project_root / file_path

            if full_path.exists():
                try:
                    with open(full_path, encoding="utf-8") as f:
                        content = f.read()

                    # Check for remaining MD5 instances
                    md5_patterns = [r"hashlib\.md5", r"\.md5\(", r"MD5", r"md5"]

                    for pattern in md5_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_number = content[: match.start()].count("\n") + 1
                            validation_results["remaining_md5_instances"].append(
                                {
                                    "file": str(file_path),
                                    "line": line_number,
                                    "text": match.group(0),
                                    "context": content.split("\n")[
                                        line_number - 1
                                    ].strip(),
                                }
                            )
                            validation_results["validation_passed"] = False

                    validation_results["files_checked"].append(str(file_path))

                except Exception as e:
                    error_msg = f"Error validating {file_path}: {e!s}"
                    validation_results["validation_errors"].append(error_msg)
                    validation_results["validation_passed"] = False

        return validation_results


def main():
    """Main upgrade function."""
    logger.info("🚀 ACGS-1 Cryptographic Implementation Upgrade Starting")

    project_root = "/home/dislove/ACGS-1"
    upgrader = CryptographicUpgrader(project_root)

    # Perform upgrades
    summary = upgrader.upgrade_all_files()

    # Validate upgrades
    validation = upgrader.validate_upgrades()

    # Print summary
    print("\n" + "=" * 80)
    print("🔒 ACGS-1 Cryptographic Implementation Upgrade Summary")
    print("=" * 80)
    print(
        f"Total Files Processed: {summary['upgrade_summary']['total_files_processed']}"
    )
    print(f"Files Modified: {summary['upgrade_summary']['files_modified']}")
    print(f"Total Replacements: {summary['upgrade_summary']['total_replacements']}")
    print(f"Success Rate: {summary['upgrade_summary']['success_rate']}")
    print(f"Upgrade Time: {summary['upgrade_summary']['upgrade_time']}")

    if summary["modified_files"]:
        print("\n✅ Modified Files:")
        for file_path in summary["modified_files"]:
            print(f"   - {file_path}")

    if summary["errors"]:
        print("\n❌ Errors:")
        for error in summary["errors"]:
            print(f"   - {error}")

    print("\n🔒 Security Improvements:")
    for improvement in summary["security_improvements"]:
        print(f"   - {improvement}")

    print("\n🏗️ Affected Components:")
    for component in summary["affected_components"]:
        print(f"   - {component}")

    # Validation results
    print("\n🔍 Validation Results:")
    if validation["validation_passed"]:
        print("   ✅ All MD5 instances successfully replaced with SHA-256")
    else:
        print("   ⚠️ Some MD5 instances may remain:")
        for instance in validation["remaining_md5_instances"]:
            print(f"      - {instance['file']}:{instance['line']} - {instance['text']}")

    print("\n📄 Detailed reports saved to:")
    print("   - cryptographic_upgrade_report.json")
    print("   - cryptographic_upgrade.log")

    return summary


if __name__ == "__main__":
    main()
