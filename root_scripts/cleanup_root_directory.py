#!/usr/bin/env python3
"""
ACGS-1 Root Directory Cleanup Script
Organizes 100+ scattered files in root directory into proper locations
"""

import json
import shutil
from datetime import datetime
from pathlib import Path


class RootDirectoryCleanup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "files_moved": {},
            "directories_created": [],
            "files_preserved": [],
            "errors": [],
        }

    def create_organized_structure(self):
        """Create organized directory structure"""
        directories = [
            "logs",
            "reports",
            "reports/analysis",
            "reports/security",
            "reports/performance",
            "reports/deployment",
            "temp",
            "archive",
            "archive/backups",
            "archive/old_reports",
            "scripts/maintenance",
            "scripts/analysis",
        ]

        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.cleanup_report["directories_created"].append(str(directory))
                print(f"✅ Created directory: {directory}")

    def categorize_and_move_files(self):
        """Categorize and move files to appropriate locations"""

        # Files to keep in root (core project files)
        keep_in_root = {
            "README.md",
            "LICENSE",
            "Cargo.toml",
            "package.json",
            "package-lock.json",
            "docker-compose.yml",
            "docker-compose.prod.yml",
            "Dockerfile.acgs",
            "Makefile",
            "pyproject.toml",
            "requirements.txt",
            "pytest.ini",
            "tsconfig.json",
            "jest.config.js",
            "conftest.py",
            "uv.lock",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
        }

        # File categorization patterns
        file_patterns = {
            "reports": [
                "*_REPORT.md",
                "*_SUMMARY.md",
                "*_PLAN.md",
                "*_GUIDE.md",
                "*_ANALYSIS.md",
                "*_COMPLETION*.md",
                "*_IMPLEMENTATION*.md",
            ],
            "reports/security": [
                "security_*.json",
                "security_*.md",
                "bandit_*.json",
                "*security*.json",
                "*_security_*.md",
            ],
            "reports/performance": [
                "performance_*.json",
                "*_performance_*.json",
                "coverage.json",
            ],
            "reports/deployment": [
                "*deployment*.json",
                "*_deployment_*.md",
                "quantumagi_*.json",
            ],
            "logs": [
                "*.log",
                "*.txt",
                "chat_history.txt",
                "cron_jobs.txt",
                "prometheus_metrics.txt",
            ],
            "temp": [
                "temp_*.prd",
                "*_temp_*",
                "debug_*.py",
                "test_*.py",
                "quick_*.py",
                "simple_*.py",
            ],
            "scripts/maintenance": [
                "cleanup_*.py",
                "fix_*.py",
                "restart_*.py",
                "start_*.py",
                "validate_*.py",
                "update_*.py",
                "apply_*.py",
            ],
            "scripts/analysis": ["analyze_*.py", "comprehensive_*.py", "final_*.py"],
            "archive": ["Tasks_*.md", "*_backup_*", "backup_*"],
        }

        # Move files based on patterns
        for root_item in self.project_root.iterdir():
            if root_item.is_file():
                filename = root_item.name

                # Skip files that should stay in root
                if filename in keep_in_root:
                    self.cleanup_report["files_preserved"].append(filename)
                    continue

                # Find appropriate destination
                moved = False
                for destination, patterns in file_patterns.items():
                    for pattern in patterns:
                        if self._matches_pattern(filename, pattern):
                            self._move_file(root_item, destination)
                            moved = True
                            break
                    if moved:
                        break

                # If no pattern matched, move to temp for manual review
                if not moved and not filename.startswith("."):
                    self._move_file(root_item, "temp")

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches pattern (simple glob-like matching)"""
        if pattern.startswith("*") and pattern.endswith("*"):
            return pattern[1:-1] in filename
        if pattern.startswith("*"):
            return filename.endswith(pattern[1:])
        if pattern.endswith("*"):
            return filename.startswith(pattern[:-1])
        return filename == pattern

    def _move_file(self, file_path: Path, destination: str):
        """Move file to destination directory"""
        try:
            dest_dir = self.project_root / destination
            dest_path = dest_dir / file_path.name

            # Handle name conflicts
            if dest_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = file_path.name.rsplit(".", 1)
                if len(name_parts) == 2:
                    new_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
                else:
                    new_name = f"{file_path.name}_{timestamp}"
                dest_path = dest_dir / new_name

            shutil.move(str(file_path), str(dest_path))
            self.cleanup_report["files_moved"][str(file_path)] = str(dest_path)
            print(f"📁 Moved: {file_path.name} → {destination}/")

        except Exception as e:
            error_msg = f"Failed to move {file_path}: {e!s}"
            self.cleanup_report["errors"].append(error_msg)
            print(f"❌ {error_msg}")

    def cleanup_backup_directories(self):
        """Consolidate backup directories"""
        backup_dirs = ["backups", "cleanup_backup_*", "reorganization_backup_*"]
        archive_backup_dir = self.project_root / "archive" / "backups"

        for item in self.project_root.iterdir():
            if item.is_dir() and any(
                self._matches_pattern(item.name, pattern) for pattern in backup_dirs
            ):
                try:
                    dest_path = archive_backup_dir / item.name
                    if dest_path.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        dest_path = archive_backup_dir / f"{item.name}_{timestamp}"

                    shutil.move(str(item), str(dest_path))
                    print(f"📦 Archived backup: {item.name} → archive/backups/")

                except Exception as e:
                    error_msg = f"Failed to move backup directory {item}: {e!s}"
                    self.cleanup_report["errors"].append(error_msg)
                    print(f"❌ {error_msg}")

    def generate_cleanup_report(self):
        """Generate cleanup completion report"""
        report_path = (
            self.project_root / "reports" / "root_directory_cleanup_report.json"
        )

        with open(report_path, "w") as f:
            json.dump(self.cleanup_report, f, indent=2)

        print(f"\n📊 Cleanup Report Generated: {report_path}")
        print(f"✅ Files moved: {len(self.cleanup_report['files_moved'])}")
        print(
            f"✅ Directories created: {len(self.cleanup_report['directories_created'])}"
        )
        print(
            f"✅ Files preserved in root: {len(self.cleanup_report['files_preserved'])}"
        )
        print(f"❌ Errors: {len(self.cleanup_report['errors'])}")

    def update_root_readme(self):
        """Update main README.md to reflect new organization"""
        readme_path = self.project_root / "README.md"

        organization_section = """

## 📁 Project Organization

After comprehensive cleanup, the project is now organized as follows:

- **Root Directory**: Core project files only (README, LICENSE, package.json, etc.)
- **`reports/`**: All analysis reports, summaries, and documentation
  - `reports/analysis/`: System analysis and audit reports
  - `reports/security/`: Security scan results and remediation reports
  - `reports/performance/`: Performance benchmarks and optimization reports
  - `reports/deployment/`: Deployment logs and validation reports
- **`logs/`**: Application logs and monitoring data
- **`temp/`**: Temporary files and work-in-progress items
- **`archive/`**: Historical files and backups
- **`scripts/`**: Organized maintenance and analysis scripts

This organization improves project maintainability and navigation.
"""

        try:
            if readme_path.exists():
                with open(readme_path, "a") as f:
                    f.write(organization_section)
                print("✅ Updated README.md with organization information")
        except Exception as e:
            print(f"❌ Failed to update README.md: {e}")

    def run_cleanup(self):
        """Execute complete cleanup process"""
        print("🧹 Starting ACGS-1 Root Directory Cleanup...")
        print("=" * 50)

        self.create_organized_structure()
        self.categorize_and_move_files()
        self.cleanup_backup_directories()
        self.generate_cleanup_report()
        self.update_root_readme()

        print("\n" + "=" * 50)
        print("🎉 Root Directory Cleanup Complete!")
        print("📁 Project structure is now organized and maintainable")


if __name__ == "__main__":
    cleanup = RootDirectoryCleanup()
    cleanup.run_cleanup()
