#!/usr/bin/env python3
"""
ACGS Large File Analysis Tool

Comprehensive analysis of large files in the ACGS project to identify:
1. Storage usage patterns and large file distribution
2. File categorization (dependencies, build artifacts, data files, etc.)
3. Cleanup opportunities and optimization recommendations
4. Performance impact analysis

Usage:
    python tools/large_file_analyzer.py [--threshold-mb SIZE] [--output-format json|table]
"""

import argparse
import hashlib
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class LargeFileAnalyzer:
    def __init__(self, project_root: str = "/home/ubuntu/ACGS", threshold_mb: int = 1):
        self.project_root = Path(project_root)
        self.threshold_bytes = threshold_mb * 1024 * 1024
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "threshold_mb": threshold_mb,
            "categories": {
                "dependencies": [],
                "git_objects": [],
                "build_artifacts": [],
                "data_files": [],
                "logs": [],
                "media": [],
                "archives": [],
                "other": [],
            },
            "size_distribution": {"1MB_10MB": [], "10MB_100MB": [], "100MB_plus": []},
            "summary": {},
        }

        # File type categorization patterns
        self.category_patterns = {
            "dependencies": [
                "node_modules/",
                "venv/",
                "target/",
                ".cargo/",
                "vendor/",
                "packages/",
                "lib/",
                "dist/",
            ],
            "git_objects": [".git/objects/", ".git/pack/"],
            "build_artifacts": [
                "build/",
                "dist/",
                "out/",
                "target/",
                ".next/",
                "__pycache__/",
                ".mypy_cache/",
                ".pytest_cache/",
            ],
            "data_files": [".db", ".sqlite", ".json", ".csv", ".xml"],
            "logs": [".log", ".out", ".err", "logs/"],
            "media": [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".avi", ".mov"],
            "archives": [".zip", ".tar", ".gz", ".bz2", ".xz", ".7z"],
        }

    def categorize_file(self, file_path: str) -> str:
        """Categorize a file based on its path and extension."""
        file_path_lower = file_path.lower()

        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if pattern in file_path_lower:
                    return category

        return "other"

    def format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}PB"

    def get_file_hash(self, file_path: Path) -> str | None:
        """Get MD5 hash of file for duplicate detection."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except OSError:
            return None

    def should_ignore_path(self, path: str) -> bool:
        """Check if path should be ignored during analysis."""
        ignore_patterns = [
            "/.git/",
            "/venv/",
            "/__pycache__/",
            "/.pytest_cache/",
            "/.mypy_cache/",
            "/node_modules/",
            "/target/debug/",
            "/target/release/",
            "/.cargo/",
            "/dist/",
            "/build/",
        ]

        for pattern in ignore_patterns:
            if pattern in path:
                return True
        return False

    def analyze_large_files(self) -> None:
        """Scan and analyze all large files in the project."""
        print(
            f"🔍 Scanning for files larger than {self.threshold_bytes / (1024 * 1024):.1f}MB..."
        )

        total_files = 0
        large_files_found = 0
        total_size = 0

        for root, dirs, files in os.walk(self.project_root):
            # Skip certain directories for performance
            dirs[:] = [
                d for d in dirs if not self.should_ignore_path(os.path.join(root, d))
            ]

            for filename in files:
                total_files += 1
                if total_files % 10000 == 0:
                    print(
                        f"   Scanned {total_files} files, found {large_files_found} large files..."
                    )

                file_path = Path(root) / filename
                try:
                    file_size = file_path.stat().st_size

                    if file_size >= self.threshold_bytes:
                        large_files_found += 1
                        total_size += file_size

                        relative_path = str(file_path.relative_to(self.project_root))
                        category = self.categorize_file(relative_path)

                        file_info = {
                            "path": relative_path,
                            "size_bytes": file_size,
                            "size_formatted": self.format_size(file_size),
                            "category": category,
                            "modified": datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat(),
                            "hash": (
                                self.get_file_hash(file_path)
                                if file_size < 100 * 1024 * 1024
                                else None
                            ),
                        }

                        # Add to category
                        self.analysis_results["categories"][category].append(file_info)

                        # Add to size distribution
                        if file_size < 10 * 1024 * 1024:
                            self.analysis_results["size_distribution"][
                                "1MB_10MB"
                            ].append(file_info)
                        elif file_size < 100 * 1024 * 1024:
                            self.analysis_results["size_distribution"][
                                "10MB_100MB"
                            ].append(file_info)
                        else:
                            self.analysis_results["size_distribution"][
                                "100MB_plus"
                            ].append(file_info)

                except OSError:
                    continue

        print(
            f"✅ Analysis complete: {large_files_found} large files found ({self.format_size(total_size)} total)"
        )

    def generate_summary(self) -> None:
        """Generate summary statistics."""
        total_files = sum(
            len(files) for files in self.analysis_results["categories"].values()
        )
        total_size = sum(
            file_info["size_bytes"]
            for files in self.analysis_results["categories"].values()
            for file_info in files
        )

        category_stats = {}
        for category, files in self.analysis_results["categories"].items():
            if files:
                category_size = sum(f["size_bytes"] for f in files)
                category_stats[category] = {
                    "count": len(files),
                    "total_size": self.format_size(category_size),
                    "percentage": (
                        (category_size / total_size * 100) if total_size > 0 else 0
                    ),
                }

        size_stats = {}
        for size_range, files in self.analysis_results["size_distribution"].items():
            if files:
                range_size = sum(f["size_bytes"] for f in files)
                size_stats[size_range] = {
                    "count": len(files),
                    "total_size": self.format_size(range_size),
                    "percentage": (
                        (range_size / total_size * 100) if total_size > 0 else 0
                    ),
                }

        self.analysis_results["summary"] = {
            "total_large_files": total_files,
            "total_size": self.format_size(total_size),
            "total_size_bytes": total_size,
            "category_breakdown": category_stats,
            "size_distribution": size_stats,
        }

    def detect_duplicates(self) -> list[dict]:
        """Detect potential duplicate files based on size and hash."""
        print("🔍 Detecting potential duplicate files...")

        size_groups = defaultdict(list)
        hash_groups = defaultdict(list)

        # Group by size first
        for category_files in self.analysis_results["categories"].values():
            for file_info in category_files:
                size_groups[file_info["size_bytes"]].append(file_info)

        # Then group by hash for same-size files
        duplicates = []
        for size, files in size_groups.items():
            if len(files) > 1:
                # Group by hash
                for file_info in files:
                    if file_info["hash"]:
                        hash_groups[file_info["hash"]].append(file_info)

        # Find actual duplicates
        for hash_val, files in hash_groups.items():
            if len(files) > 1:
                duplicates.append(
                    {
                        "hash": hash_val,
                        "files": files,
                        "potential_savings": self.format_size(
                            (len(files) - 1) * files[0]["size_bytes"]
                        ),
                    }
                )

        return duplicates

    def generate_recommendations(self) -> list[dict]:
        """Generate cleanup and optimization recommendations."""
        recommendations = []

        # Check for large dependency directories
        deps = self.analysis_results["categories"]["dependencies"]
        if deps:
            deps_size = sum(f["size_bytes"] for f in deps)
            if deps_size > 1024 * 1024 * 1024:  # > 1GB
                recommendations.append(
                    {
                        "type": "CLEANUP",
                        "priority": "HIGH",
                        "title": "Large dependency directories detected",
                        "description": f"Dependencies taking up {self.format_size(deps_size)}. Consider cleaning node_modules, target, or venv directories.",
                        "files": [f["path"] for f in deps[:5]],  # Show top 5
                    }
                )

        # Check for large build artifacts
        artifacts = self.analysis_results["categories"]["build_artifacts"]
        if artifacts:
            artifacts_size = sum(f["size_bytes"] for f in artifacts)
            if artifacts_size > 100 * 1024 * 1024:  # > 100MB
                recommendations.append(
                    {
                        "type": "CLEANUP",
                        "priority": "MEDIUM",
                        "title": "Large build artifacts detected",
                        "description": f"Build artifacts taking up {self.format_size(artifacts_size)}. These can usually be safely removed and regenerated.",
                        "files": [f["path"] for f in artifacts[:5]],
                    }
                )

        # Check for very large individual files
        huge_files = self.analysis_results["size_distribution"]["100MB_plus"]
        if huge_files:
            recommendations.append(
                {
                    "type": "REVIEW",
                    "priority": "HIGH",
                    "title": "Very large files detected",
                    "description": f"{len(huge_files)} files larger than 100MB found. Review if these are necessary.",
                    "files": [f["path"] for f in huge_files],
                }
            )

        return recommendations

    def print_table_report(self) -> None:
        """Print analysis results in table format."""
        print("\n" + "=" * 80)
        print("📊 ACGS LARGE FILE ANALYSIS REPORT")
        print("=" * 80)

        summary = self.analysis_results["summary"]
        print("\n📈 SUMMARY:")
        print(f"   Total large files: {summary['total_large_files']}")
        print(f"   Total size: {summary['total_size']}")
        print(f"   Analysis threshold: {self.analysis_results['threshold_mb']}MB")

        print("\n📂 BY CATEGORY:")
        for category, stats in summary["category_breakdown"].items():
            print(
                f"   {category:15} {stats['count']:4d} files  {stats['total_size']:>10}  ({stats['percentage']:5.1f}%)"
            )

        print("\n📏 BY SIZE RANGE:")
        for size_range, stats in summary["size_distribution"].items():
            range_name = size_range.replace("_", "-").replace("plus", "+")
            print(
                f"   {range_name:15} {stats['count']:4d} files  {stats['total_size']:>10}  ({stats['percentage']:5.1f}%)"
            )

        # Show top 10 largest files
        all_files = []
        for files in self.analysis_results["categories"].values():
            all_files.extend(files)

        top_files = sorted(all_files, key=lambda x: x["size_bytes"], reverse=True)[:10]

        print("\n🔝 TOP 10 LARGEST FILES:")
        for i, file_info in enumerate(top_files, 1):
            print(f"   {i:2d}. {file_info['size_formatted']:>8} {file_info['path']}")

        # Show recommendations
        recommendations = self.generate_recommendations()
        if recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in recommendations:
                print(f"   [{rec['priority']}] {rec['title']}")
                print(f"       {rec['description']}")

        # Show duplicates
        duplicates = self.detect_duplicates()
        if duplicates:
            print("\n🔄 POTENTIAL DUPLICATES:")
            for dup in duplicates[:5]:  # Show top 5
                print(
                    f"   {len(dup['files'])} files, potential savings: {dup['potential_savings']}"
                )
                for file_info in dup["files"][:3]:  # Show first 3 files
                    print(f"     - {file_info['path']}")

    def save_json_report(self, output_file: str) -> None:
        """Save analysis results to JSON file."""
        # Add recommendations and duplicates to results
        self.analysis_results["recommendations"] = self.generate_recommendations()
        self.analysis_results["duplicates"] = self.detect_duplicates()

        with open(output_file, "w") as f:
            json.dump(self.analysis_results, f, indent=2)

        print(f"📄 Detailed analysis saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Analyze large files in ACGS project")
    parser.add_argument(
        "--threshold-mb",
        type=int,
        default=1,
        help="Minimum file size in MB to analyze (default: 1)",
    )
    parser.add_argument(
        "--output-format",
        choices=["json", "table"],
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument("--output-file", type=str, help="Output file for JSON format")

    args = parser.parse_args()

    analyzer = LargeFileAnalyzer(threshold_mb=args.threshold_mb)
    analyzer.analyze_large_files()
    analyzer.generate_summary()

    if args.output_format == "table":
        analyzer.print_table_report()

    if args.output_format == "json" or args.output_file:
        output_file = (
            args.output_file
            or f"large_file_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        analyzer.save_json_report(output_file)


if __name__ == "__main__":
    main()
