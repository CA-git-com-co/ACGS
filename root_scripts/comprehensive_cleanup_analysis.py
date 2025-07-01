#!/usr/bin/env python3
"""
ACGS-1 Comprehensive Cleanup Analysis Tool

This script performs a comprehensive analysis of the ACGS-1 project to identify:
1. Duplicate files (exact and similar)
2. Obsolete code and configurations
3. Non-functional files and broken links
4. Files safe for removal while preserving critical components

PRESERVATION REQUIREMENTS:
- Quantumagi Solana deployment files
- Enhancement framework in services/shared/enhancement_framework/
- All 7 core services and their dependencies
- Constitutional governance files with hash cdd01ef066bc6cf2
- Blockchain-related files in blockchain/ directory
- Database migrations, schemas, and configuration files
"""

import os
import sys
import json
import hashlib
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
import difflib


class ACGSCleanupAnalyzer:
    def __init__(self, project_root: str = "/home/dislove/ACGS-1"):
        self.project_root = Path(project_root)
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "duplicates": {
                "exact_duplicates": [],
                "similar_files": [],
                "version_variants": [],
            },
            "obsolete_files": {
                "deprecated_services": [],
                "old_configs": [],
                "backup_files": [],
                "temp_files": [],
            },
            "non_functional": {
                "broken_symlinks": [],
                "empty_directories": [],
                "import_errors": [],
                "missing_dependencies": [],
            },
            "preservation_critical": {
                "quantumagi": [],
                "enhancement_framework": [],
                "core_services": [],
                "constitutional": [],
                "blockchain": [],
                "database": [],
            },
            "cleanup_recommendations": {
                "safe_to_remove": [],
                "consolidate": [],
                "move_to_correct_location": [],
                "update_references": [],
            },
        }

        # Critical preservation patterns
        self.critical_patterns = {
            "quantumagi": [
                "blockchain/quantumagi-deployment/",
                "quantumagi",
                "constitution_data.json",
                "governance_accounts.json",
                "initial_policies.json",
            ],
            "enhancement_framework": ["services/shared/enhancement_framework/"],
            "core_services": [
                "services/core/constitutional-ai/",
                "services/core/governance-synthesis/",
                "services/core/formal-verification/",
                "services/core/policy-governance/",
                "services/core/evolutionary-computation/",
                "services/core/self-evolving-ai/",
            ],
            "constitutional": ["cdd01ef066bc6cf2", "constitutional", "constitution"],
            "blockchain": [
                "blockchain/programs/",
                "blockchain/Anchor.toml",
                "blockchain/Cargo.toml",
            ],
            "database": ["alembic/", "migrations/", "models.py", "schema"],
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def is_critical_file(self, file_path: Path) -> Tuple[bool, str]:
        """Check if file is critical and should be preserved."""
        file_str = str(file_path)

        for category, patterns in self.critical_patterns.items():
            for pattern in patterns:
                if pattern in file_str:
                    return True, category
        return False, ""

    def find_exact_duplicates(self) -> Dict[str, List[str]]:
        """Find files with identical content."""
        hash_to_files = {}

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self.should_skip_file(file_path):
                file_hash = self.calculate_file_hash(file_path)
                if file_hash:
                    if file_hash not in hash_to_files:
                        hash_to_files[file_hash] = []
                    hash_to_files[file_hash].append(str(file_path))

        # Return only groups with duplicates
        duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
        return duplicates

    def find_similar_files(self) -> List[Dict]:
        """Find files with similar names but different content."""
        similar_groups = []
        files_by_name = {}

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self.should_skip_file(file_path):
                base_name = file_path.stem
                if base_name not in files_by_name:
                    files_by_name[base_name] = []
                files_by_name[base_name].append(file_path)

        for base_name, files in files_by_name.items():
            if len(files) > 1:
                # Check if they're actually different
                hashes = set()
                for file_path in files:
                    file_hash = self.calculate_file_hash(file_path)
                    hashes.add(file_hash)

                if len(hashes) > 1:  # Different content
                    similar_groups.append(
                        {
                            "base_name": base_name,
                            "files": [str(f) for f in files],
                            "count": len(files),
                        }
                    )

        return similar_groups

    def should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped in analysis."""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            ".git",
            "node_modules",
            "venv",
            "target/debug",
            "target/release",
            ".log",
            "test-ledger",
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def analyze_duplicates(self):
        """Analyze duplicate files."""
        print("🔍 Analyzing duplicate files...")

        # Find exact duplicates
        exact_duplicates = self.find_exact_duplicates()
        for file_hash, files in exact_duplicates.items():
            # Check if any are critical
            critical_files = []
            non_critical_files = []

            for file_path in files:
                is_critical, category = self.is_critical_file(Path(file_path))
                if is_critical:
                    critical_files.append({"path": file_path, "category": category})
                else:
                    non_critical_files.append(file_path)

            self.analysis_results["duplicates"]["exact_duplicates"].append(
                {
                    "hash": file_hash,
                    "files": files,
                    "critical_files": critical_files,
                    "non_critical_files": non_critical_files,
                    "recommendation": (
                        "Keep critical files, remove non-critical duplicates"
                        if critical_files
                        else "Keep one, remove others"
                    ),
                }
            )

        # Find similar files
        similar_files = self.find_similar_files()
        self.analysis_results["duplicates"]["similar_files"] = similar_files

        print(f"✅ Found {len(exact_duplicates)} exact duplicate groups")
        print(f"✅ Found {len(similar_files)} similar file groups")

    def find_version_variants(self) -> List[Dict]:
        """Find files that appear to be different versions of the same component."""
        version_patterns = [
            r"(.+)_v(\d+)",
            r"(.+)_enhanced",
            r"(.+)_new",
            r"(.+)_old",
            r"(.+)_backup",
            r"(.+)_copy",
            r"(.+)_fixed",
            r"(.+)_updated",
        ]

        variants = []
        for pattern in version_patterns:
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file():
                    match = re.search(pattern, file_path.stem)
                    if match:
                        base_name = match.group(1)
                        # Look for other variants
                        related_files = []
                        for other_file in self.project_root.rglob(f"{base_name}*"):
                            if other_file.is_file() and other_file != file_path:
                                related_files.append(str(other_file))

                        if related_files:
                            variants.append(
                                {
                                    "base_name": base_name,
                                    "variant": str(file_path),
                                    "related_files": related_files,
                                }
                            )

        return variants

    def analyze_obsolete_files(self):
        """Analyze potentially obsolete files."""
        print("🗑️ Analyzing obsolete files...")

        obsolete_patterns = {
            "backup_files": [".bak", ".backup", "_backup", ".old", "_old"],
            "temp_files": [".tmp", ".temp", "_temp", ".swp", "~"],
            "log_files": [".log"],
            "cache_files": ["__pycache__", ".pyc", ".pyo"],
            "build_artifacts": ["target/debug", "target/release", "node_modules"],
        }

        for category, patterns in obsolete_patterns.items():
            files = []
            for pattern in patterns:
                for file_path in self.project_root.rglob(f"*{pattern}*"):
                    if file_path.exists():
                        is_critical, _ = self.is_critical_file(file_path)
                        if not is_critical:
                            files.append(str(file_path))

            self.analysis_results["obsolete_files"][category] = files

    def analyze_non_functional(self):
        """Analyze non-functional files and directories."""
        print("🔧 Analyzing non-functional files...")

        # Find broken symlinks
        for file_path in self.project_root.rglob("*"):
            if file_path.is_symlink() and not file_path.exists():
                self.analysis_results["non_functional"]["broken_symlinks"].append(
                    str(file_path)
                )

        # Find empty directories
        for dir_path in self.project_root.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                # Skip if it's a critical directory that might be intentionally empty
                is_critical, _ = self.is_critical_file(dir_path)
                if not is_critical:
                    self.analysis_results["non_functional"]["empty_directories"].append(
                        str(dir_path)
                    )

    def catalog_critical_files(self):
        """Catalog all critical files that must be preserved."""
        print("🛡️ Cataloging critical files...")

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                is_critical, category = self.is_critical_file(file_path)
                if is_critical:
                    self.analysis_results["preservation_critical"][category].append(
                        str(file_path)
                    )

    def generate_cleanup_recommendations(self):
        """Generate specific cleanup recommendations."""
        print("💡 Generating cleanup recommendations...")

        # Recommend exact duplicates for removal
        for dup_group in self.analysis_results["duplicates"]["exact_duplicates"]:
            if dup_group["non_critical_files"]:
                self.analysis_results["cleanup_recommendations"][
                    "safe_to_remove"
                ].extend(
                    dup_group["non_critical_files"][1:]  # Keep first, remove rest
                )

        # Recommend obsolete files for removal
        for category, files in self.analysis_results["obsolete_files"].items():
            if category in ["backup_files", "temp_files", "cache_files"]:
                self.analysis_results["cleanup_recommendations"][
                    "safe_to_remove"
                ].extend(files)

    def run_full_analysis(self):
        """Run complete cleanup analysis."""
        print("🚀 Starting comprehensive ACGS-1 cleanup analysis...")

        self.analyze_duplicates()
        self.analyze_obsolete_files()
        self.analyze_non_functional()
        self.catalog_critical_files()
        self.generate_cleanup_recommendations()

        # Generate summary
        summary = {
            "total_exact_duplicates": len(
                self.analysis_results["duplicates"]["exact_duplicates"]
            ),
            "total_similar_files": len(
                self.analysis_results["duplicates"]["similar_files"]
            ),
            "total_obsolete_files": sum(
                len(files) for files in self.analysis_results["obsolete_files"].values()
            ),
            "total_safe_to_remove": len(
                self.analysis_results["cleanup_recommendations"]["safe_to_remove"]
            ),
            "critical_files_preserved": sum(
                len(files)
                for files in self.analysis_results["preservation_critical"].values()
            ),
        }

        self.analysis_results["summary"] = summary

        print(f"📊 Analysis complete:")
        print(f"   - {summary['total_exact_duplicates']} exact duplicate groups")
        print(f"   - {summary['total_similar_files']} similar file groups")
        print(f"   - {summary['total_obsolete_files']} obsolete files")
        print(f"   - {summary['total_safe_to_remove']} files safe to remove")
        print(f"   - {summary['critical_files_preserved']} critical files preserved")


if __name__ == "__main__":
    analyzer = ACGSCleanupAnalyzer()
    analyzer.run_full_analysis()

    # Save results
    output_file = (
        f"acgs_cleanup_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    with open(output_file, "w") as f:
        json.dump(analyzer.analysis_results, f, indent=2)

    print(f"📊 Complete analysis saved to {output_file}")
