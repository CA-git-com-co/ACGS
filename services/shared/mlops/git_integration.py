"""
Git Integration for MLOps

Provides Git integration capabilities for tracking code changes,
configuration updates, and automated tagging for model versions.

This module integrates with the ACGS-PGP system to provide full
traceability from code changes to model deployments.
"""

import logging
import subprocess
import json
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class GitError(Exception):
    """Raised when Git operations fail."""

    pass


@dataclass
class CommitInfo:
    """Information about a Git commit."""

    hash: str
    short_hash: str
    author: str
    email: str
    timestamp: datetime
    message: str
    branch: str
    files_changed: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "hash": self.hash,
            "short_hash": self.short_hash,
            "author": self.author,
            "email": self.email,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "branch": self.branch,
            "files_changed": self.files_changed,
        }


@dataclass
class TagInfo:
    """Information about a Git tag."""

    name: str
    commit_hash: str
    tagger: str
    timestamp: datetime
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "commit_hash": self.commit_hash,
            "tagger": self.tagger,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
        }


class GitIntegration:
    """
    Git integration for MLOps operations.

    Provides functionality to track code changes, create tags,
    and maintain traceability for model versions.
    """

    def __init__(
        self, repo_path: str = ".", constitutional_hash: str = "cdd01ef066bc6cf2"
    ):
        self.repo_path = Path(repo_path)
        self.constitutional_hash = constitutional_hash

        # Verify Git repository
        if not self._is_git_repo():
            raise GitError(f"Not a Git repository: {repo_path}")

        logger.info(f"GitIntegration initialized for repo: {repo_path}")

    def _is_git_repo(self) -> bool:
        """Check if directory is a Git repository."""
        git_dir = self.repo_path / ".git"
        return git_dir.exists()

    def _run_git_command(self, command: List[str]) -> str:
        """Run Git command and return output."""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(f"Git command failed: {e.stderr}")

    def get_current_commit(self) -> CommitInfo:
        """Get information about the current commit."""
        try:
            # Get commit hash
            commit_hash = self._run_git_command(["rev-parse", "HEAD"])
            short_hash = self._run_git_command(["rev-parse", "--short", "HEAD"])

            # Get commit details
            commit_info = self._run_git_command(
                ["show", "--format=%an|%ae|%ct|%s", "--name-only", commit_hash]
            )

            lines = commit_info.split("\n")
            author_line = lines[0]
            author, email, timestamp_str, message = author_line.split("|", 3)

            # Get current branch
            try:
                branch = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
            except GitError:
                branch = "detached"

            # Get changed files
            files_changed = [line for line in lines[2:] if line.strip()]

            # Convert timestamp
            timestamp = datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)

            return CommitInfo(
                hash=commit_hash,
                short_hash=short_hash,
                author=author,
                email=email,
                timestamp=timestamp,
                message=message,
                branch=branch,
                files_changed=files_changed,
            )

        except Exception as e:
            raise GitError(f"Failed to get current commit info: {e}")

    def get_commit_by_hash(self, commit_hash: str) -> CommitInfo:
        """Get information about a specific commit."""
        try:
            # Get commit details
            commit_info = self._run_git_command(
                ["show", "--format=%an|%ae|%ct|%s", "--name-only", commit_hash]
            )

            lines = commit_info.split("\n")
            author_line = lines[0]
            author, email, timestamp_str, message = author_line.split("|", 3)

            # Get short hash
            short_hash = self._run_git_command(["rev-parse", "--short", commit_hash])

            # Get branch (may not be accurate for historical commits)
            try:
                branch = self._run_git_command(
                    ["branch", "--contains", commit_hash, "--format=%(refname:short)"]
                ).split("\n")[0]
            except GitError:
                branch = "unknown"

            # Get changed files
            files_changed = [line for line in lines[2:] if line.strip()]

            # Convert timestamp
            timestamp = datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)

            return CommitInfo(
                hash=commit_hash,
                short_hash=short_hash,
                author=author,
                email=email,
                timestamp=timestamp,
                message=message,
                branch=branch,
                files_changed=files_changed,
            )

        except Exception as e:
            raise GitError(f"Failed to get commit info for {commit_hash}: {e}")

    def create_tag(
        self, tag_name: str, message: str, commit_hash: Optional[str] = None
    ) -> TagInfo:
        """
        Create a Git tag for model version tracking.

        Args:
            tag_name: Name of the tag
            message: Tag message
            commit_hash: Specific commit to tag (defaults to HEAD)

        Returns:
            TagInfo: Information about the created tag
        """

        logger.info(f"Creating Git tag: {tag_name}")

        try:
            # Create annotated tag
            tag_command = ["tag", "-a", tag_name, "-m", message]
            if commit_hash:
                tag_command.append(commit_hash)

            self._run_git_command(tag_command)

            # Get tag information
            tag_info = self._run_git_command(["show", "--format=%an|%ct", tag_name])

            lines = tag_info.split("\n")
            tagger_line = lines[0]
            tagger, timestamp_str = tagger_line.split("|", 1)

            # Get commit hash for tag
            tagged_commit = self._run_git_command(["rev-list", "-n", "1", tag_name])

            # Convert timestamp
            timestamp = datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)

            tag_info_obj = TagInfo(
                name=tag_name,
                commit_hash=tagged_commit,
                tagger=tagger,
                timestamp=timestamp,
                message=message,
            )

            logger.info(f"Created tag {tag_name} at commit {tagged_commit[:8]}")
            return tag_info_obj

        except Exception as e:
            raise GitError(f"Failed to create tag {tag_name}: {e}")

    def get_tag_info(self, tag_name: str) -> TagInfo:
        """Get information about a specific tag."""
        try:
            # Get tag information
            tag_info = self._run_git_command(["show", "--format=%an|%ct", tag_name])

            lines = tag_info.split("\n")
            tagger_line = lines[0]
            tagger, timestamp_str = tagger_line.split("|", 1)

            # Get commit hash for tag
            tagged_commit = self._run_git_command(["rev-list", "-n", "1", tag_name])

            # Get tag message
            try:
                message = self._run_git_command(
                    ["tag", "-l", "--format=%(contents)", tag_name]
                )
            except GitError:
                message = ""

            # Convert timestamp
            timestamp = datetime.fromtimestamp(int(timestamp_str), tz=timezone.utc)

            return TagInfo(
                name=tag_name,
                commit_hash=tagged_commit,
                tagger=tagger,
                timestamp=timestamp,
                message=message,
            )

        except Exception as e:
            raise GitError(f"Failed to get tag info for {tag_name}: {e}")

    def list_tags(self, pattern: Optional[str] = None) -> List[TagInfo]:
        """List all tags, optionally filtered by pattern."""
        try:
            # Get tag list
            tag_command = ["tag", "-l"]
            if pattern:
                tag_command.append(pattern)

            tag_names = self._run_git_command(tag_command).split("\n")
            tag_names = [name.strip() for name in tag_names if name.strip()]

            # Get info for each tag
            tags = []
            for tag_name in tag_names:
                try:
                    tag_info = self.get_tag_info(tag_name)
                    tags.append(tag_info)
                except GitError as e:
                    logger.warning(f"Failed to get info for tag {tag_name}: {e}")

            return sorted(tags, key=lambda t: t.timestamp, reverse=True)

        except Exception as e:
            raise GitError(f"Failed to list tags: {e}")

    def get_changes_since_commit(self, commit_hash: str) -> List[str]:
        """Get list of files changed since a specific commit."""
        try:
            changed_files = self._run_git_command(
                ["diff", "--name-only", commit_hash, "HEAD"]
            )

            return [f.strip() for f in changed_files.split("\n") if f.strip()]

        except Exception as e:
            raise GitError(f"Failed to get changes since {commit_hash}: {e}")

    def is_working_directory_clean(self) -> bool:
        """Check if working directory has uncommitted changes."""
        try:
            status = self._run_git_command(["status", "--porcelain"])
            return len(status.strip()) == 0
        except GitError:
            return False

    def get_repository_info(self) -> Dict[str, Any]:
        """Get general repository information."""
        try:
            current_commit = self.get_current_commit()
            is_clean = self.is_working_directory_clean()

            # Get remote URL
            try:
                remote_url = self._run_git_command(["remote", "get-url", "origin"])
            except GitError:
                remote_url = "unknown"

            return {
                "repo_path": str(self.repo_path),
                "current_commit": current_commit.to_dict(),
                "is_clean": is_clean,
                "remote_url": remote_url,
                "constitutional_hash": self.constitutional_hash,
                "constitutional_hash_verified": self.constitutional_hash
                == "cdd01ef066bc6cf2",
            }

        except Exception as e:
            raise GitError(f"Failed to get repository info: {e}")


class GitTracker:
    """
    High-level Git tracking for MLOps workflows.

    Provides simplified interface for common Git operations
    in the context of model versioning and deployment.
    """

    def __init__(
        self, repo_path: str = ".", constitutional_hash: str = "cdd01ef066bc6cf2"
    ):
        self.git = GitIntegration(repo_path, constitutional_hash)
        self.constitutional_hash = constitutional_hash

        logger.info("GitTracker initialized")

    def track_model_version(
        self, model_name: str, version: str, performance_metrics: Dict[str, float]
    ) -> TagInfo:
        """
        Create Git tag for model version with metadata.

        Args:
            model_name: Name of the model
            version: Model version string
            performance_metrics: Model performance metrics

        Returns:
            TagInfo: Information about the created tag
        """

        tag_name = f"{model_name}-v{version}"

        # Create tag message with metadata
        message_data = {
            "model_name": model_name,
            "version": version,
            "performance_metrics": performance_metrics,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        message = f"Model version {version} for {model_name}\n\n"
        message += json.dumps(message_data, indent=2)

        return self.git.create_tag(tag_name, message)

    def get_model_version_history(self, model_name: str) -> List[TagInfo]:
        """Get version history for a specific model."""
        pattern = f"{model_name}-v*"
        return self.git.list_tags(pattern)

    def validate_deployment_readiness(self) -> Dict[str, Any]:
        """
        Validate that repository is ready for deployment.

        Returns:
            Dict with validation results
        """

        repo_info = self.git.get_repository_info()
        current_commit = self.git.get_current_commit()

        validation_results = {
            "is_ready": True,
            "issues": [],
            "repo_info": repo_info,
            "current_commit": current_commit.to_dict(),
            "constitutional_hash_verified": self.constitutional_hash
            == "cdd01ef066bc6cf2",
        }

        # Check if working directory is clean
        if not repo_info["is_clean"]:
            validation_results["is_ready"] = False
            validation_results["issues"].append(
                "Working directory has uncommitted changes"
            )

        # Check constitutional hash
        if not validation_results["constitutional_hash_verified"]:
            validation_results["is_ready"] = False
            validation_results["issues"].append(
                f"Invalid constitutional hash: {self.constitutional_hash}"
            )

        # Check if on main/master branch for production deployments
        if current_commit.branch not in ["main", "master", "production"]:
            validation_results["issues"].append(
                f"Not on production branch (current: {current_commit.branch})"
            )

        logger.info(
            f"Deployment readiness validation: {'PASSED' if validation_results['is_ready'] else 'FAILED'}"
        )

        return validation_results
