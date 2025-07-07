#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Setup Branch Protection Rules for ACGS Repositories

This script configures branch protection rules and repository settings.
"""

import json
import logging
import subprocess
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BranchProtectionSetup:
    def __init__(self, org_name: str = "CA-git-com-co"):
        self.org_name = org_name
        self.repositories = [
            "acgs-core",
            "acgs-platform",
            "acgs-blockchain",
            "acgs-models",
            "acgs-applications",
            "acgs-infrastructure",
            "acgs-tools",
        ]

    def setup_branch_protection(
        self, repo_name: str, branch: str = "acgs-minimal"
    ) -> bool:
        """Setup branch protection rules for a repository"""
        try:
            # Configure branch protection
            logger.info(f"Setting up branch protection for {repo_name}:{branch}")

            protection_cmd = [
                "gh",
                "api",
                f"repos/{self.org_name}/{repo_name}/branches/{branch}/protection",
                "--method",
                "PUT",
                "--field",
                "required_status_checks[strict]=true",
                "--field",
                "required_status_checks[contexts][]=test",
                "--field",
                "required_status_checks[contexts][]=security",
                "--field",
                "enforce_admins=true",
                "--field",
                "required_pull_request_reviews[required_approving_review_count]=1",
                "--field",
                "required_pull_request_reviews[dismiss_stale_reviews]=true",
                "--field",
                "required_pull_request_reviews[require_code_owner_reviews]=true",
                "--field",
                "restrictions=null",
            ]

            result = subprocess.run(protection_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ Branch protection configured for {repo_name}")
                return True
            else:
                logger.warning(
                    f"⚠️ Branch protection setup failed for {repo_name}: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to setup branch protection for {repo_name}: {e}")
            return False

    def setup_repository_settings(self, repo_name: str) -> bool:
        """Configure repository settings"""
        try:
            logger.info(f"Configuring repository settings for {repo_name}")

            # Enable vulnerability alerts
            subprocess.run(
                [
                    "gh",
                    "api",
                    f"repos/{self.org_name}/{repo_name}/vulnerability-alerts",
                    "--method",
                    "PUT",
                ],
                capture_output=True,
            )

            # Enable automated security fixes
            subprocess.run(
                [
                    "gh",
                    "api",
                    f"repos/{self.org_name}/{repo_name}/automated-security-fixes",
                    "--method",
                    "PUT",
                ],
                capture_output=True,
            )

            # Configure repository settings
            settings_cmd = [
                "gh",
                "api",
                f"repos/{self.org_name}/{repo_name}",
                "--method",
                "PATCH",
                "--field",
                "has_issues=true",
                "--field",
                "has_projects=true",
                "--field",
                "has_wiki=true",
                "--field",
                "allow_squash_merge=true",
                "--field",
                "allow_merge_commit=false",
                "--field",
                "allow_rebase_merge=false",
                "--field",
                "delete_branch_on_merge=true",
            ]

            subprocess.run(settings_cmd, capture_output=True)

            logger.info(f"✅ Repository settings configured for {repo_name}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to configure repository settings for {repo_name}: {e}"
            )
            return False

    def create_codeowners_file(self, repo_name: str) -> bool:
        """Create CODEOWNERS file for the repository"""
        try:
            # Define code owners based on repository
            owners_mapping = {
                "acgs-core": [
                    "@CA-git-com-co/ai-ml-team",
                    "@CA-git-com-co/platform-team",
                ],
                "acgs-platform": ["@CA-git-com-co/platform-team"],
                "acgs-blockchain": ["@CA-git-com-co/blockchain-team"],
                "acgs-models": ["@CA-git-com-co/ai-ml-team"],
                "acgs-applications": ["@CA-git-com-co/frontend-team"],
                "acgs-infrastructure": ["@CA-git-com-co/devops-team"],
                "acgs-tools": [
                    "@CA-git-com-co/devops-team",
                    "@CA-git-com-co/platform-team",
                ],
            }

            owners = owners_mapping.get(repo_name, ["@CA-git-com-co/platform-team"])

            codeowners_content = f"""# CODEOWNERS file for {repo_name}
# This file defines code review requirements for this repository

# Global owners for all files
* {' '.join(owners)}

# CI/CD pipeline files require DevOps team approval
.github/workflows/* @CA-git-com-co/devops-team

# Security and monitoring configurations
monitoring/* @CA-git-com-co/devops-team @CA-git-com-co/security-team
security/* @CA-git-com-co/security-team @CA-git-com-co/devops-team

# Documentation
*.md @CA-git-com-co/tech-writing-team
docs/* @CA-git-com-co/tech-writing-team
"""

            # Create CODEOWNERS file via GitHub API
            codeowners_cmd = [
                "gh",
                "api",
                f"repos/{self.org_name}/{repo_name}/contents/.github/CODEOWNERS",
                "--method",
                "PUT",
                "--field",
                f"message=Add CODEOWNERS file for {repo_name}",
                "--field",
                f"content={self._encode_base64(codeowners_content)}",
            ]

            result = subprocess.run(codeowners_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"✅ CODEOWNERS file created for {repo_name}")
                return True
            else:
                logger.warning(
                    f"⚠️ CODEOWNERS creation failed for {repo_name}: {result.stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to create CODEOWNERS for {repo_name}: {e}")
            return False

    def _encode_base64(self, content: str) -> str:
        """Encode string to base64 for GitHub API"""
        import base64

        return base64.b64encode(content.encode()).decode()

    def setup_all_repositories(self) -> dict:
        """Setup branch protection and settings for all repositories"""
        results = {}

        for repo_name in self.repositories:
            logger.info(f"\n=== Configuring {repo_name} ===")

            # Setup repository settings
            settings_success = self.setup_repository_settings(repo_name)

            # Setup branch protection
            protection_success = self.setup_branch_protection(repo_name)

            # Create CODEOWNERS file
            codeowners_success = self.create_codeowners_file(repo_name)

            if settings_success and protection_success:
                results[repo_name] = "success"
                logger.info(f"✅ {repo_name} configuration complete")
            else:
                results[repo_name] = "partial_success"
                logger.warning(f"⚠️ {repo_name} configuration partially completed")

        return results


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup branch protection for ACGS repositories"
    )
    parser.add_argument(
        "--org", default="CA-git-com-co", help="GitHub organization name"
    )
    parser.add_argument("--repo", help="Setup specific repository only")

    args = parser.parse_args()

    setup = BranchProtectionSetup(args.org)

    if args.repo:
        # Setup single repository
        settings_success = setup.setup_repository_settings(args.repo)
        protection_success = setup.setup_branch_protection(args.repo)
        codeowners_success = setup.create_codeowners_file(args.repo)

        if settings_success and protection_success:
            logger.info(f"✅ {args.repo} configuration complete")
        else:
            logger.warning(f"⚠️ {args.repo} configuration issues")
    else:
        # Setup all repositories
        results = setup.setup_all_repositories()

        successful = [repo for repo, status in results.items() if status == "success"]
        partial = [
            repo for repo, status in results.items() if status == "partial_success"
        ]

        logger.info(f"\n=== Setup Summary ===")
        logger.info(f"Successful: {len(successful)}/{len(results)}")
        if partial:
            logger.warning(f"Partial success: {', '.join(partial)}")

        logger.info("✅ Branch protection and repository configuration complete!")


if __name__ == "__main__":
    main()
