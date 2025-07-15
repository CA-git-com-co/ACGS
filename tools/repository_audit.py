#!/usr/bin/env python3
"""
ACGS-2 Repository Size and Hygiene Audit Script

This script:
1. Audits repository for large files
2. Identifies artifacts that shouldn't be version controlled
3. Analyzes .gitignore patterns
4. Recommends Git LFS candidates
5. Cleans up repository structure

Usage:
    python scripts/repository_audit.py [--fix] [--dry-run]
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class RepositoryAuditor:
    """Audits repository size and hygiene."""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.report = {
            "large_files": [],
            "artifacts": [],
            "gitignore_improvements": [],
            "lfs_candidates": [],
            "cleanup_actions": [],
        }

        # File size thresholds (in bytes)
        self.LARGE_FILE_THRESHOLD = 10 * 1024 * 1024  # 10MB
        self.LFS_THRESHOLD = 50 * 1024 * 1024  # 50MB

        # Patterns for artifacts that shouldn't be versioned
        self.ARTIFACT_PATTERNS = [
            "*.pyc",
            "*.pyo",
            "*.pyd",
            "__pycache__",
            "*.log",
            "*.tmp",
            "*.temp",
            "coverage.xml",
            "coverage.json",
            "htmlcov",
            ".pytest_cache",
            ".coverage",
            "*.egg-info",
            "build",
            "dist",
            "node_modules",
            ".npm",
            "target",
            "*.class",
            "*.jar",
            ".DS_Store",
            "Thumbs.db",
            "*.swp",
            "*.swo",
            "*~",
            ".vscode",
            ".idea",
            "bandit-report.json",
        ]

        # Extensions that should use Git LFS
        self.LFS_EXTENSIONS = {
            ".pkl",
            ".joblib",
            ".model",
            ".weights",
            ".bin",
            ".dat",
            ".db",
            ".sqlite",
            ".zip",
            ".tar.gz",
            ".7z",
            ".mp4",
            ".avi",
            ".mov",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".pdf",
            ".doc",
            ".docx",
            ".ppt",
            ".pptx",
        }

    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        try:
            return file_path.stat().st_size
        except (OSError, FileNotFoundError):
            return 0

    def find_large_files(self) -> list[dict[str, any]]:
        """Find files larger than threshold."""
        large_files = []

        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not self._should_skip_path(file_path):
                size = self.get_file_size(file_path)

                if size > self.LARGE_FILE_THRESHOLD:
                    large_files.append(
                        {
                            "path": str(file_path.relative_to(self.project_root)),
                            "size_bytes": size,
                            "size_mb": round(size / (1024 * 1024), 2),
                            "lfs_candidate": size > self.LFS_THRESHOLD
                            or file_path.suffix in self.LFS_EXTENSIONS,
                        }
                    )

        # Sort by size descending
        large_files.sort(key=lambda x: x["size_bytes"], reverse=True)
        return large_files

    def find_artifacts(self) -> list[dict[str, any]]:
        """Find artifacts that shouldn't be version controlled."""
        artifacts = []

        for pattern in self.ARTIFACT_PATTERNS:
            # Use glob to find matching files
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file():
                    artifacts.append(
                        {
                            "path": str(file_path.relative_to(self.project_root)),
                            "pattern": pattern,
                            "size_bytes": self.get_file_size(file_path),
                        }
                    )

        return artifacts

    def analyze_gitignore(self) -> list[str]:
        """Analyze .gitignore and suggest improvements."""
        gitignore_path = self.project_root / ".gitignore"
        improvements = []

        # Read current .gitignore
        current_patterns = set()
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                current_patterns = {
                    line.strip()
                    for line in f
                    if line.strip() and not line.startswith("#")
                }

        # Recommended patterns
        recommended_patterns = {
            # Python
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            ".Python",
            "build/",
            "develop-eggs/",
            "dist/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            # Virtual environments
            "config/environments/development.env",
            ".venv",
            "env/",
            "venv/",
            "ENV/",
            "env.bak/",
            "venv.bak/",
            # Testing and coverage
            ".pytest_cache/",
            ".coverage",
            "reports/coverage/htmlcov/",
            "coverage.xml",
            "coverage.json",
            ".tox/",
            ".nox/",
            ".cache",
            "nosetests.xml",
            "*.cover",
            ".hypothesis/",
            # Jupyter Notebook
            ".ipynb_checkpoints",
            # IDEs
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
            # OS
            ".DS_Store",
            "Thumbs.db",
            # Logs
            "*.log",
            "logs/",
            # Temporary files
            "*.tmp",
            "*.temp",
            "tmp/",
            "temp/",
            # Security
            "config/environments/development.env.local",
            "config/environments/development.env.*.local",
            "*.pem",
            "*.key",
            # Build artifacts
            "node_modules/",
            ".npm",
            "target/",
            "*.class",
            # Large files and models
            "*.model",
            "*.weights",
            "*.pkl",
            "*.joblib",
            # Reports
            "bandit-report.json",
            "security-report.json",
        }

        # Find missing patterns
        missing_patterns = recommended_patterns - current_patterns
        if missing_patterns:
            improvements.extend(sorted(missing_patterns))

        return improvements

    def get_repository_size(self) -> dict[str, any]:
        """Get repository size information."""
        try:
            # Get git repository size
            result = subprocess.run(
                ["git", "count-objects", "-vH"],
                check=False,
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            size_info = {}
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        size_info[key.strip()] = value.strip()

            return size_info

        except subprocess.SubprocessError:
            return {"error": "Could not get repository size"}

    def _should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped."""
        skip_patterns = [
            ".git",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "htmlcov",
            "build",
            "dist",
        ]

        path_str = str(path)
        return any(pattern in path_str for pattern in skip_patterns)

    def update_gitignore(self, improvements: list[str]) -> None:
        """Update .gitignore with improvements."""
        gitignore_path = self.project_root / ".gitignore"

        if not improvements:
            return

        # Read current content
        current_content = ""
        if gitignore_path.exists():
            current_content = gitignore_path.read_text()

        # Add improvements
        new_content = current_content
        if not current_content.endswith("\n") and current_content:
            new_content += "\n"

        new_content += "\n# Additional patterns for better repository hygiene\n"
        for pattern in improvements:
            new_content += f"{pattern}\n"

        if not self.dry_run:
            gitignore_path.write_text(new_content)
            print(f"✅ Updated .gitignore with {len(improvements)} new patterns")
        else:
            print(f"Would add {len(improvements)} patterns to .gitignore")

    def setup_git_lfs(self, lfs_candidates: list[dict[str, any]]) -> None:
        """Set up Git LFS for large files."""
        if not lfs_candidates:
            return

        # Check if Git LFS is available
        try:
            subprocess.run(["git", "lfs", "version"], capture_output=True, check=True)
        except (subprocess.SubprocessError, FileNotFoundError):
            print("⚠️  Git LFS not available. Install with: git lfs install")
            return

        # Get unique extensions from LFS candidates
        extensions = set()
        for candidate in lfs_candidates:
            path = Path(candidate["path"])
            if path.suffix:
                extensions.add(path.suffix)

        if not self.dry_run:
            # Track extensions with Git LFS
            for ext in extensions:
                try:
                    subprocess.run(
                        ["git", "lfs", "track", f"*{ext}"],
                        cwd=self.project_root,
                        check=True,
                    )
                    print(f"✅ Added {ext} files to Git LFS tracking")
                except subprocess.SubprocessError as e:
                    print(f"❌ Failed to track {ext} with Git LFS: {e}")
        else:
            print(
                f"Would track {len(extensions)} file extensions with Git LFS: {', '.join(extensions)}"
            )

    def clean_artifacts(self, artifacts: list[dict[str, any]]) -> None:
        """Clean up artifacts that shouldn't be versioned."""
        if not artifacts:
            return

        cleaned_count = 0
        for artifact in artifacts:
            file_path = self.project_root / artifact["path"]

            if file_path.exists():
                if not self.dry_run:
                    try:
                        file_path.unlink()
                        cleaned_count += 1
                    except OSError as e:
                        print(f"❌ Failed to remove {artifact['path']}: {e}")
                else:
                    cleaned_count += 1

        if not self.dry_run:
            print(f"✅ Cleaned up {cleaned_count} artifact files")
        else:
            print(f"Would clean up {cleaned_count} artifact files")

    def run_audit(self, apply_fixes: bool = False) -> dict[str, any]:
        """Run complete repository audit."""
        print("🔍 Starting ACGS-2 Repository Audit")
        print("=" * 50)

        # Find large files
        print("\n📊 Analyzing file sizes...")
        self.report["large_files"] = self.find_large_files()

        # Find artifacts
        print("🗑️  Finding artifacts...")
        self.report["artifacts"] = self.find_artifacts()

        # Analyze .gitignore
        print("📝 Analyzing .gitignore...")
        self.report["gitignore_improvements"] = self.analyze_gitignore()

        # Identify LFS candidates
        self.report["lfs_candidates"] = [
            f for f in self.report["large_files"] if f["lfs_candidate"]
        ]

        # Get repository size
        repo_size = self.get_repository_size()

        # Print summary
        print("\n📋 Audit Summary:")
        print(
            f"  Large files (>{self.LARGE_FILE_THRESHOLD // (1024 * 1024)}MB): {len(self.report['large_files'])}"
        )
        print(f"  Artifacts to clean: {len(self.report['artifacts'])}")
        print(f"  Git LFS candidates: {len(self.report['lfs_candidates'])}")
        print(
            f"  .gitignore improvements: {len(self.report['gitignore_improvements'])}"
        )

        if repo_size and "size" in repo_size:
            print(f"  Repository size: {repo_size.get('size', 'unknown')}")

        # Apply fixes if requested
        if apply_fixes:
            print("\n🔧 Applying fixes...")

            # Update .gitignore
            if self.report["gitignore_improvements"]:
                self.update_gitignore(self.report["gitignore_improvements"])

            # Set up Git LFS
            if self.report["lfs_candidates"]:
                self.setup_git_lfs(self.report["lfs_candidates"])

            # Clean artifacts
            if self.report["artifacts"]:
                self.clean_artifacts(self.report["artifacts"])

        return self.report


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Audit ACGS-2 repository size and hygiene"
    )
    parser.add_argument("--fix", action="store_true", help="Apply fixes automatically")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Default to dry run unless --fix is specified
    dry_run = not args.fix or args.dry_run

    project_root = Path(__file__).parent.parent
    auditor = RepositoryAuditor(project_root, dry_run=dry_run)

    report = auditor.run_audit(apply_fixes=args.fix)

    # Print detailed report
    if report["large_files"]:
        print("\n📊 Large Files:")
        for file_info in report["large_files"][:10]:  # Show top 10
            lfs_marker = " (LFS candidate)" if file_info["lfs_candidate"] else ""
            print(f"  {file_info['path']}: {file_info['size_mb']}MB{lfs_marker}")

    if report["gitignore_improvements"]:
        print("\n📝 Suggested .gitignore additions:")
        for pattern in report["gitignore_improvements"][:10]:  # Show first 10
            print(f"  {pattern}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
