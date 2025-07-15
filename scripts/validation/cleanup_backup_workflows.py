#!/usr/bin/env python3
"""
Clean up backup workflow files with syntax errors

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import shutil
from pathlib import Path
from typing import List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def identify_backup_workflows(project_root: Path) -> List[Path]:
    """Identify backup workflow files."""
    workflow_dir = project_root / ".github" / "workflows"
    backup_files = []

    # Find backup files
    backup_patterns = ["*.backup", "*backup*"]
    for pattern in backup_patterns:
        backup_files.extend(workflow_dir.glob(pattern))

    # Also find backup directories
    for item in workflow_dir.iterdir():
        if item.is_dir() and "backup" in item.name.lower():
            backup_files.append(item)

    return backup_files


def validate_backup_files(project_root: Path) -> Tuple[bool, List[str]]:
    """Validate backup files and identify ones with syntax errors."""
    issues = []

    try:
        import yaml
    except ImportError:
        issues.append("PyYAML not available - skipping validation")
        return True, issues

    backup_files = identify_backup_workflows(project_root)

    for backup_file in backup_files:
        if backup_file.is_file() and backup_file.suffix in ['.yml', '.yaml']:
            try:
                content = backup_file.read_text(encoding='utf-8')
                yaml.safe_load(content)
                issues.append(f"✅ Valid YAML: {backup_file.name}")
            except yaml.YAMLError as e:
                issues.append(f"❌ YAML error in {backup_file.name}: {str(e)[:100]}...")
            except Exception as e:
                issues.append(f"⚠️  Error reading {backup_file.name}: {e}")
        elif backup_file.is_dir():
            issues.append(f"📁 Backup directory: {backup_file.name}")

    return True, issues


def archive_backup_files(project_root: Path) -> Tuple[bool, List[str]]:
    """Archive backup workflow files to keep the workflows directory clean."""
    issues = []

    # Create archive directory
    archive_dir = project_root / "archive" / "workflows"
    archive_dir.mkdir(parents=True, exist_ok=True)

    backup_files = identify_backup_workflows(project_root)

    for backup_file in backup_files:
        try:
            if backup_file.is_file():
                # Move file to archive
                dest = archive_dir / backup_file.name
                shutil.move(str(backup_file), str(dest))
                issues.append(f"📦 Archived file: {backup_file.name}")
            elif backup_file.is_dir():
                # Move directory to archive
                dest = archive_dir / backup_file.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(backup_file), str(dest))
                issues.append(f"📦 Archived directory: {backup_file.name}")
        except Exception as e:
            issues.append(f"❌ Error archiving {backup_file.name}: {e}")

    return len([issue for issue in issues if "❌" in issue]) == 0, issues


def main():
    """Main cleanup function."""
    project_root = Path(__file__).parent.parent.parent

    print("🧹 Cleaning Up Backup Workflow Files")
    print(f"📁 Project root: {project_root}")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    all_passed = True

    # Run cleanup steps
    steps = [
        ("Validate Backup Files", validate_backup_files),
        ("Archive Backup Files", archive_backup_files)
    ]

    for step_name, step_func in steps:
        print(f"🔍 {step_name}...")
        passed, issues = step_func(project_root)

        if passed:
            print(f"✅ {step_name}: COMPLETED")
        else:
            print(f"❌ {step_name}: FAILED")
            all_passed = False

        for issue in issues:
            print(f"   {issue}")
        print()

    # Summary
    if all_passed:
        print("🎉 Backup workflow cleanup COMPLETED!")
        print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("\n✅ Workflows directory is now clean and organized")
        return 0

    print("⚠️  Some cleanup steps FAILED!")
    print("Please address the issues above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())