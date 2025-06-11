#!/usr/bin/env python3
"""
Emergency rollback script for dependency merges
Use if any merge causes critical issues
"""

import logging
import subprocess
import sys
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmergencyRollback:
    """Emergency rollback procedures"""

    def __init__(self):
        self.rollback_commands = {
            "httpx": {
                "description": "Rollback httpx upgrade (PR #102)",
                "commands": [
                    "git log --oneline -10",  # Show recent commits
                    "git revert HEAD --no-edit",  # Revert last commit
                    "git push origin master",  # Push rollback
                ],
            },
            "mimesis": {
                "description": "Rollback mimesis upgrade (PR #104)",
                "commands": [
                    "git log --oneline -10",
                    "git revert HEAD --no-edit",
                    "git push origin master",
                ],
            },
            "anthropic": {
                "description": "Rollback anthropic upgrade (PR #107)",
                "commands": [
                    "git log --oneline -10",
                    "git revert HEAD --no-edit",
                    "git push origin master",
                ],
            },
        }

    def check_git_status(self) -> Dict[str, Any]:
        """Check current git status"""
        logger.info("📊 Checking git status...")

        try:
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )

            # Get recent commits
            log_result = subprocess.run(
                ["git", "log", "--oneline", "-5"], capture_output=True, text=True
            )

            # Check for uncommitted changes
            status_result = subprocess.run(
                ["git", "status", "--porcelain"], capture_output=True, text=True
            )

            return {
                "status": "success",
                "current_branch": branch_result.stdout.strip(),
                "recent_commits": log_result.stdout.strip().split("\n"),
                "uncommitted_changes": len(status_result.stdout.strip()) > 0,
                "uncommitted_files": (
                    status_result.stdout.strip().split("\n")
                    if status_result.stdout.strip()
                    else []
                ),
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def execute_rollback(self, dependency: str, dry_run: bool = True) -> Dict[str, Any]:
        """Execute rollback for specific dependency"""
        logger.info(
            f"🔄 {'Simulating' if dry_run else 'Executing'} rollback for {dependency}..."
        )

        if dependency not in self.rollback_commands:
            return {"status": "error", "error": f"Unknown dependency: {dependency}"}

        rollback_info = self.rollback_commands[dependency]
        results = {
            "dependency": dependency,
            "description": rollback_info["description"],
            "dry_run": dry_run,
            "command_results": [],
        }

        for command in rollback_info["commands"]:
            try:
                if dry_run:
                    # In dry run, just show what would be executed
                    results["command_results"].append(
                        {
                            "command": command,
                            "status": "dry_run",
                            "message": f"Would execute: {command}",
                        }
                    )
                else:
                    # Actually execute the command
                    result = subprocess.run(
                        command.split(), capture_output=True, text=True, timeout=60
                    )

                    results["command_results"].append(
                        {
                            "command": command,
                            "status": "success" if result.returncode == 0 else "failed",
                            "return_code": result.returncode,
                            "output": result.stdout[-500:] if result.stdout else "",
                            "errors": result.stderr[-500:] if result.stderr else "",
                        }
                    )

            except Exception as e:
                results["command_results"].append(
                    {"command": command, "status": "error", "error": str(e)}
                )

        return results

    def validate_rollback(self) -> Dict[str, Any]:
        """Validate system after rollback"""
        logger.info("✅ Validating system after rollback...")

        try:
            # Run basic health check
            result = subprocess.run(
                ["python", "post_merge_validation.py"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            return {
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "validation_passed": result.returncode == 0,
                "output": result.stdout[-1000:] if result.stdout else "",
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}


def main():
    """Main rollback execution"""
    if len(sys.argv) < 2:
        print("Usage: python emergency_rollback.py <dependency> [--execute]")
        print("Dependencies: httpx, mimesis, anthropic")
        print("Add --execute to actually perform rollback (default is dry-run)")
        sys.exit(1)

    dependency = sys.argv[1].lower()
    execute = "--execute" in sys.argv

    rollback = EmergencyRollback()

    # Check git status first
    git_status = rollback.check_git_status()

    print("\n" + "=" * 60)
    print("EMERGENCY ROLLBACK PROCEDURE")
    print("=" * 60)
    print(f"Target Dependency: {dependency.upper()}")
    print(f"Mode: {'EXECUTE' if execute else 'DRY RUN'}")
    print(f"Current Branch: {git_status.get('current_branch', 'unknown')}")
    print("=" * 60)

    if git_status.get("uncommitted_changes"):
        print("⚠️ WARNING: Uncommitted changes detected!")
        print("Files with changes:")
        for file in git_status.get("uncommitted_files", []):
            print(f"  {file}")
        print("Consider committing or stashing changes before rollback")
        print("=" * 60)

    # Show recent commits
    print("Recent commits:")
    for commit in git_status.get("recent_commits", []):
        print(f"  {commit}")
    print("=" * 60)

    if not execute:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("Add --execute flag to perform actual rollback")
        print("=" * 60)

    # Execute rollback
    rollback_result = rollback.execute_rollback(dependency, dry_run=not execute)

    print(f"\nRollback Results for {dependency}:")
    print(f"Description: {rollback_result.get('description', 'N/A')}")

    for cmd_result in rollback_result.get("command_results", []):
        command = cmd_result["command"]
        status = cmd_result["status"]
        print(f"  {command}: {status.upper()}")

        if status == "error" and "error" in cmd_result:
            print(f"    Error: {cmd_result['error']}")
        elif status == "failed" and "return_code" in cmd_result:
            print(f"    Return code: {cmd_result['return_code']}")
            if cmd_result.get("errors"):
                print(f"    Errors: {cmd_result['errors']}")

    # Validate if rollback was executed
    if execute:
        print("\n" + "=" * 60)
        print("VALIDATING ROLLBACK...")
        print("=" * 60)

        validation_result = rollback.validate_rollback()

        if validation_result.get("validation_passed"):
            print("✅ ROLLBACK SUCCESSFUL")
            print("   System validation passed after rollback")
        else:
            print("❌ ROLLBACK VALIDATION FAILED")
            print("   Manual intervention may be required")
            print(f"   Validation output: {validation_result.get('output', 'N/A')}")

    print("=" * 60)


if __name__ == "__main__":
    main()
