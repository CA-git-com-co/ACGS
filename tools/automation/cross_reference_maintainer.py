#!/usr/bin/env python3
"""
ACGS Automated Cross-Reference Maintenance Tool
Constitutional Hash: cdd01ef066bc6cf2

This tool automatically maintains cross-references when files are moved, renamed,
or deleted. It monitors git operations and updates documentation links automatically.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Link patterns to track
LINK_PATTERNS = {
    "markdown_link": r"\[([^\]]+)\]\(([^)]+)\)",
    "reference_link": r"\[([^\]]+)\]:\s*([^\s]+)",
    "relative_path": r"(?:\.{1,2}/)+[^)\s]+",
    "file_reference": r'(?:src/|services/|docs/|tools/|tests/)[^)\s\'"]+',
    "code_import": r'(?:import|from)\s+["\']([^"\']+)["\']',
    "include_directive": r"!\[.*?\]\(([^)]+)\)",
    "yaml_reference": r'(?:file|path|src):\s*["\']?([^"\'>\s]+)["\']?',
    "config_path": r'(?:config|template|schema).*?["\']([^"\']+)["\']',
}

# File extensions to scan
SCANNABLE_EXTENSIONS = {
    ".md",
    ".py",
    ".js",
    ".ts",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".rst",
    ".sh",
    ".dockerfile",
    ".tf",
    ".toml",
}


class CrossReferenceTracker:
    """Tracks cross-references across the entire repository."""

    def __init__(self):
        self.reference_map: Dict[str, Set[str]] = {}
        self.reverse_map: Dict[str, Set[str]] = {}
        self.last_scan_time = None
        self.cache_file = REPO_ROOT / ".cross_reference_cache.json"
        self.load_cache()

    def load_cache(self):
        """Load cached reference mappings."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    data = json.load(f)
                    self.reference_map = {
                        k: set(v) for k, v in data.get("reference_map", {}).items()
                    }
                    self.reverse_map = {
                        k: set(v) for k, v in data.get("reverse_map", {}).items()
                    }
                    self.last_scan_time = data.get("last_scan_time")
            except (json.JSONDecodeError, IOError):
                print("Warning: Could not load cross-reference cache")

    def save_cache(self):
        """Save reference mappings to cache."""
        try:
            data = {
                "reference_map": {k: list(v) for k, v in self.reference_map.items()},
                "reverse_map": {k: list(v) for k, v in self.reverse_map.items()},
                "last_scan_time": self.last_scan_time,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }
            with open(self.cache_file, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save cross-reference cache: {e}")

    def scan_repository(self, force_rescan: bool = False) -> None:
        """Scan the entire repository for cross-references."""
        if not force_rescan and self.last_scan_time:
            # Check if we need to rescan based on git changes
            last_commit_time = self._get_last_commit_time()
            if last_commit_time <= self.last_scan_time:
                print("Repository unchanged since last scan, using cache")
                return

        print("Scanning repository for cross-references...")
        start_time = time.time()

        self.reference_map.clear()
        self.reverse_map.clear()

        # Find all scannable files
        files_to_scan = []
        for ext in SCANNABLE_EXTENSIONS:
            files_to_scan.extend(REPO_ROOT.rglob(f"*{ext}"))

        # Filter out hidden directories and common ignore patterns
        files_to_scan = [
            f
            for f in files_to_scan
            if not any(part.startswith(".") for part in f.parts[len(REPO_ROOT.parts) :])
            and "node_modules" not in f.parts
            and "__pycache__" not in f.parts
        ]

        print(f"Scanning {len(files_to_scan)} files...")

        # Use thread pool for parallel scanning
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_file = {
                executor.submit(self._scan_file, f): f for f in files_to_scan
            }

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    references = future.result()
                    if references:
                        rel_path = str(file_path.relative_to(REPO_ROOT))
                        self.reference_map[rel_path] = references

                        # Build reverse mapping
                        for ref in references:
                            if ref not in self.reverse_map:
                                self.reverse_map[ref] = set()
                            self.reverse_map[ref].add(rel_path)

                except Exception as e:
                    print(f"Error scanning {file_path}: {e}")

        self.last_scan_time = time.time()
        self.save_cache()

        scan_duration = time.time() - start_time
        print(f"Scan completed in {scan_duration:.2f}s")
        print(f"Found {len(self.reference_map)} files with references")
        print(
            f"Tracking {sum(len(refs) for refs in self.reference_map.values())} total references"
        )

    def _get_last_commit_time(self) -> Optional[float]:
        """Get the timestamp of the last git commit."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%ct"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except (subprocess.SubprocessError, ValueError):
            pass
        return None

    def _scan_file(self, file_path: Path) -> Set[str]:
        """Scan a single file for cross-references."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            references = set()

            # Apply all link patterns
            for pattern_name, pattern in LINK_PATTERNS.items():
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for match in matches:
                    # Extract the reference (usually the second group for links)
                    if pattern_name in [
                        "markdown_link",
                        "reference_link",
                        "include_directive",
                    ]:
                        ref = (
                            match.group(2)
                            if len(match.groups()) >= 2
                            else match.group(1)
                        )
                    else:
                        ref = match.group(1) if match.groups() else match.group(0)

                    # Normalize and validate reference
                    ref = self._normalize_reference(ref, file_path)
                    if ref and self._is_internal_reference(ref):
                        references.add(ref)

            return references

        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return set()

    def _normalize_reference(self, ref: str, source_file: Path) -> Optional[str]:
        """Normalize a reference to a standard format."""
        if not ref or ref.startswith(("http://", "https://", "mailto:", "ftp://")):
            return None

        # Remove anchors and query parameters
        ref = re.sub(r"[#?].*$", "", ref)

        # Resolve relative paths
        if ref.startswith("./") or ref.startswith("../"):
            try:
                resolved = (source_file.parent / ref).resolve().relative_to(REPO_ROOT)
                return str(resolved)
            except (ValueError, OSError):
                return None

        # Handle absolute paths within repo
        if ref.startswith("/"):
            ref = ref[1:]

        # Ensure the path exists or could exist
        potential_path = REPO_ROOT / ref
        if potential_path.exists() or any(
            potential_path.with_suffix(ext).exists()
            for ext in [".md", ".py", ".js", ".ts", ""]
        ):
            return ref

        return None

    def _is_internal_reference(self, ref: str) -> bool:
        """Check if a reference is internal to the repository."""
        return not ref.startswith(("http://", "https://", "mailto:", "ftp://"))

    def update_references(self, old_path: str, new_path: str) -> List[str]:
        """Update all references when a file is moved or renamed."""
        print(f"Updating references: {old_path} → {new_path}")

        # Find all files that reference the old path
        referencing_files = self.reverse_map.get(old_path, set())
        updated_files = []

        for ref_file in referencing_files:
            try:
                if self._update_file_references(ref_file, old_path, new_path):
                    updated_files.append(ref_file)
            except Exception as e:
                print(f"Error updating {ref_file}: {e}")

        # Update internal mappings
        self._update_internal_mappings(old_path, new_path)

        return updated_files

    def _update_file_references(
        self, file_path: str, old_ref: str, new_ref: str
    ) -> bool:
        """Update references in a specific file."""
        full_path = REPO_ROOT / file_path
        if not full_path.exists():
            return False

        try:
            content = full_path.read_text(encoding="utf-8")
            original_content = content

            # Update different types of references
            content = self._update_markdown_links(content, old_ref, new_ref)
            content = self._update_relative_paths(content, old_ref, new_ref, full_path)
            content = self._update_import_statements(content, old_ref, new_ref)
            content = self._update_yaml_references(content, old_ref, new_ref)

            # Write back if changed
            if content != original_content:
                full_path.write_text(content, encoding="utf-8")
                print(f"  Updated: {file_path}")
                return True

        except (IOError, UnicodeDecodeError) as e:
            print(f"  Error updating {file_path}: {e}")

        return False

    def _update_markdown_links(self, content: str, old_ref: str, new_ref: str) -> str:
        """Update markdown-style links."""
        # Update [text](old_ref) to [text](new_ref)
        pattern = rf"\[([^\]]+)\]\({re.escape(old_ref)}\)"
        replacement = rf"[\1]({new_ref})"
        content = re.sub(pattern, replacement, content)

        # Update [text]: old_ref to [text]: new_ref
        pattern = rf"\[([^\]]+)\]:\s*{re.escape(old_ref)}"
        replacement = rf"[\1]: {new_ref}"
        content = re.sub(pattern, replacement, content)

        return content

    def _update_relative_paths(
        self, content: str, old_ref: str, new_ref: str, source_file: Path
    ) -> str:
        """Update relative path references."""
        # Calculate relative path from source to new location
        try:
            source_dir = source_file.parent
            old_abs = REPO_ROOT / old_ref
            new_abs = REPO_ROOT / new_ref

            old_rel = str(old_abs.relative_to(source_dir))
            new_rel = str(new_abs.relative_to(source_dir))

            # Update relative references
            content = content.replace(old_rel, new_rel)
            content = content.replace(f"./{old_rel}", f"./{new_rel}")

        except (ValueError, OSError):
            pass

        return content

    def _update_import_statements(
        self, content: str, old_ref: str, new_ref: str
    ) -> str:
        """Update import statements in code files."""
        # Python imports
        old_module = old_ref.replace("/", ".").replace(".py", "")
        new_module = new_ref.replace("/", ".").replace(".py", "")

        patterns = [
            (rf"from\s+{re.escape(old_module)}\s+import", f"from {new_module} import"),
            (rf"import\s+{re.escape(old_module)}", f"import {new_module}"),
            (rf'from\s+["\']({re.escape(old_ref)})["\']', rf'from "{new_ref}"'),
            (rf'import\s+["\']({re.escape(old_ref)})["\']', rf'import "{new_ref}"'),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        return content

    def _update_yaml_references(self, content: str, old_ref: str, new_ref: str) -> str:
        """Update YAML file references."""
        patterns = [
            (
                rf'((?:file|path|src|template|config):\s*["\']?){re.escape(old_ref)}(["\']?)',
                rf"\1{new_ref}\2",
            ),
            (rf'(- ["\']?){re.escape(old_ref)}(["\']?)', rf"\1{new_ref}\2"),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        return content

    def _update_internal_mappings(self, old_path: str, new_path: str) -> None:
        """Update internal reference mappings."""
        # Update reference_map
        if old_path in self.reference_map:
            self.reference_map[new_path] = self.reference_map.pop(old_path)

        # Update reverse_map
        if old_path in self.reverse_map:
            self.reverse_map[new_path] = self.reverse_map.pop(old_path)

        # Update references to this file in other files' mappings
        for file_refs in self.reference_map.values():
            if old_path in file_refs:
                file_refs.remove(old_path)
                file_refs.add(new_path)

        self.save_cache()

    def validate_references(self) -> Dict[str, List[str]]:
        """Validate all cross-references and find broken links."""
        print("Validating cross-references...")
        broken_refs = {}

        for file_path, references in self.reference_map.items():
            file_broken_refs = []

            for ref in references:
                ref_path = REPO_ROOT / ref
                if not ref_path.exists():
                    # Try with common extensions
                    found = False
                    for ext in [".md", ".py", ".js", ".ts", ""]:
                        if ref_path.with_suffix(ext).exists():
                            found = True
                            break

                    if not found:
                        file_broken_refs.append(ref)

            if file_broken_refs:
                broken_refs[file_path] = file_broken_refs

        return broken_refs

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive cross-reference report."""
        broken_refs = self.validate_references()

        report = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "summary": {
                "total_files_with_references": len(self.reference_map),
                "total_references": sum(
                    len(refs) for refs in self.reference_map.values()
                ),
                "broken_references": sum(len(refs) for refs in broken_refs.values()),
                "files_with_broken_references": len(broken_refs),
            },
            "broken_references": broken_refs,
            "top_referenced_files": self._get_top_referenced_files(10),
            "orphaned_files": self._find_orphaned_files(),
        }

        return report

    def _get_top_referenced_files(self, limit: int) -> List[Tuple[str, int]]:
        """Get the most referenced files."""
        ref_counts = [(path, len(refs)) for path, refs in self.reverse_map.items()]
        return sorted(ref_counts, key=lambda x: x[1], reverse=True)[:limit]

    def _find_orphaned_files(self) -> List[str]:
        """Find files that are not referenced by any other files."""
        all_files = set()
        for ext in SCANNABLE_EXTENSIONS:
            for f in REPO_ROOT.rglob(f"*{ext}"):
                rel_path = str(f.relative_to(REPO_ROOT))
                if not any(
                    part.startswith(".") for part in f.parts[len(REPO_ROOT.parts) :]
                ):
                    all_files.add(rel_path)

        referenced_files = set(self.reverse_map.keys())
        return list(all_files - referenced_files)


class GitHookManager:
    """Manages git hooks for automatic cross-reference maintenance."""

    def __init__(self, tracker: CrossReferenceTracker):
        self.tracker = tracker
        self.hooks_dir = REPO_ROOT / ".git" / "hooks"

    def install_hooks(self) -> None:
        """Install git hooks for automatic maintenance."""
        if not self.hooks_dir.exists():
            print("Warning: .git/hooks directory not found")
            return

        # Pre-commit hook to detect file moves/renames
        pre_commit_script = """#!/bin/bash
# ACGS Cross-Reference Maintenance Hook
# Constitutional Hash: cdd01ef066bc6cf2

# Check for renamed/moved files
python3 tools/automation/cross_reference_maintainer.py --git-hook-mode=pre-commit
"""

        # Post-commit hook to update references
        post_commit_script = """#!/bin/bash
# ACGS Cross-Reference Maintenance Hook
# Constitutional Hash: cdd01ef066bc6cf2

# Update cross-references after commit
python3 tools/automation/cross_reference_maintainer.py --git-hook-mode=post-commit
"""

        self._install_hook("pre-commit", pre_commit_script)
        self._install_hook("post-commit", post_commit_script)

        print("Git hooks installed successfully")

    def _install_hook(self, hook_name: str, script_content: str) -> None:
        """Install a specific git hook."""
        hook_path = self.hooks_dir / hook_name

        try:
            hook_path.write_text(script_content)
            hook_path.chmod(0o755)
            print(f"Installed {hook_name} hook")
        except IOError as e:
            print(f"Error installing {hook_name} hook: {e}")

    def handle_git_changes(self, mode: str) -> None:
        """Handle git changes based on hook mode."""
        if mode == "pre-commit":
            self._handle_pre_commit()
        elif mode == "post-commit":
            self._handle_post_commit()

    def _handle_pre_commit(self) -> None:
        """Handle pre-commit hook - detect file moves."""
        try:
            # Get staged changes
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-status"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                changes = result.stdout.strip().split("\n")
                renames = []

                for change in changes:
                    if change.startswith("R"):
                        # Renamed file: R100    old_path    new_path
                        parts = change.split("\t")
                        if len(parts) >= 3:
                            old_path = parts[1]
                            new_path = parts[2]
                            renames.append((old_path, new_path))

                # Store renames for post-commit processing
                if renames:
                    rename_file = REPO_ROOT / ".git" / "pending_renames.json"
                    with open(rename_file, "w") as f:
                        json.dump(renames, f)

                    print(f"Detected {len(renames)} file renames/moves")

        except subprocess.SubprocessError as e:
            print(f"Error in pre-commit hook: {e}")

    def _handle_post_commit(self) -> None:
        """Handle post-commit hook - update references."""
        rename_file = REPO_ROOT / ".git" / "pending_renames.json"

        if not rename_file.exists():
            return

        try:
            with open(rename_file, "r") as f:
                renames = json.load(f)

            for old_path, new_path in renames:
                updated_files = self.tracker.update_references(old_path, new_path)
                if updated_files:
                    print(
                        f"Updated {len(updated_files)} files for {old_path} → {new_path}"
                    )

            # Clean up
            rename_file.unlink()

            # Auto-commit reference updates if any
            if renames:
                subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, capture_output=True)

                subprocess.run(
                    [
                        "git",
                        "commit",
                        "-m",
                        f"docs: Auto-update cross-references for file moves\n\nConstitutional Hash: {CONSTITUTIONAL_HASH}",
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                )

        except (IOError, json.JSONDecodeError, subprocess.SubprocessError) as e:
            print(f"Error in post-commit hook: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="ACGS Cross-Reference Maintenance Tool"
    )
    parser.add_argument(
        "--scan", action="store_true", help="Scan repository for cross-references"
    )
    parser.add_argument(
        "--force-rescan", action="store_true", help="Force full repository rescan"
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate all cross-references"
    )
    parser.add_argument(
        "--report", action="store_true", help="Generate comprehensive report"
    )
    parser.add_argument(
        "--install-hooks", action="store_true", help="Install git hooks"
    )
    parser.add_argument(
        "--update-refs",
        nargs=2,
        metavar=("OLD_PATH", "NEW_PATH"),
        help="Update references from old path to new path",
    )
    parser.add_argument(
        "--git-hook-mode",
        choices=["pre-commit", "post-commit"],
        help="Run in git hook mode",
    )
    parser.add_argument("--output", "-o", type=str, help="Output file for report")

    args = parser.parse_args()

    # Initialize tracker
    tracker = CrossReferenceTracker()

    if args.git_hook_mode:
        # Git hook mode
        hook_manager = GitHookManager(tracker)
        hook_manager.handle_git_changes(args.git_hook_mode)
        return

    if args.install_hooks:
        hook_manager = GitHookManager(tracker)
        hook_manager.install_hooks()
        return

    if args.scan or args.force_rescan:
        tracker.scan_repository(force_rescan=args.force_rescan)

    if args.update_refs:
        old_path, new_path = args.update_refs
        updated_files = tracker.update_references(old_path, new_path)
        print(f"Updated {len(updated_files)} files")
        for file_path in updated_files:
            print(f"  - {file_path}")

    if args.validate:
        broken_refs = tracker.validate_references()
        if broken_refs:
            print(f"\nFound {len(broken_refs)} files with broken references:")
            for file_path, refs in broken_refs.items():
                print(f"  {file_path}:")
                for ref in refs:
                    print(f"    - {ref}")
        else:
            print("All cross-references are valid ✅")

    if args.report:
        report = tracker.generate_report()

        if args.output:
            with open(args.output, "w") as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output}")
        else:
            print("\n" + "=" * 60)
            print("ACGS Cross-Reference Report")
            print("=" * 60)
            print(f"Constitutional Hash: {report['constitutional_hash']}")
            print(f"Generated: {report['timestamp']}")
            print(f"\nSummary:")
            for key, value in report["summary"].items():
                print(f"  {key.replace('_', ' ').title()}: {value}")

            if report["broken_references"]:
                print(f"\nBroken References:")
                for file_path, refs in list(report["broken_references"].items())[:5]:
                    print(f"  {file_path}: {len(refs)} broken")
                if len(report["broken_references"]) > 5:
                    print(
                        f"  ... and {len(report['broken_references']) - 5} more files"
                    )

    if not any(
        [
            args.scan,
            args.force_rescan,
            args.validate,
            args.report,
            args.install_hooks,
            args.update_refs,
        ]
    ):
        parser.print_help()


if __name__ == "__main__":
    main()
